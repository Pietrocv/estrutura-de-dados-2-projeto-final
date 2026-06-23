from __future__ import annotations

from contextlib import redirect_stdout
from html import escape
from io import StringIO
from math import cos, pi, sin, sqrt

from src.analysis import detectar_triangulos, nomear_topicos
from src.communities import detect_communities, dfs_components
from src.preprocessing import preprocess_feedbacks
from src.prim_max import prim_maximum_spanning_tree
from src.similarity_graph import (
    LIMIAR_RELEVANCIA,
    calcular_densidade,
    calcular_grau_medio,
    calcular_graus,
    construir_matriz_adjacencia,
)


PALETA = [
    "#0f766e",
    "#2563eb",
    "#d97706",
    "#7c3aed",
    "#dc2626",
    "#059669",
    "#9333ea",
    "#0891b2",
    "#be123c",
    "#4d7c0f",
    "#64748b",
    "#ea580c",
]


TOPICOS_ALEATORIOS = [
    {
        "termos": ["comunicacao", "alinhamento", "retorno", "mensagem", "reuniao", "clareza", "pauta", "registro"],
        "modelos": [
            "A comunicacao teve retorno claro nas mensagens e ajudou no alinhamento da reuniao.",
            "O alinhamento da pauta deixou o combinado mais claro para os participantes.",
            "As mensagens de retorno registraram expectativas e reduziram duvidas da reuniao.",
        ],
    },
    {
        "termos": ["prazo", "cronograma", "entrega", "etapa", "atraso", "marco", "previsao", "planejamento"],
        "modelos": [
            "O prazo da entrega ficou claro no cronograma com etapas e marcos definidos.",
            "A previsao de cada data ajudou no planejamento e reduziu risco de atraso.",
            "Os marcos de entrega facilitaram acompanhar prazo, etapa e planejamento.",
        ],
    },
    {
        "termos": ["qualidade", "tecnico", "codigo", "teste", "validacao", "erro", "modulo", "consistencia"],
        "modelos": [
            "A qualidade tecnica apareceu no codigo organizado, nos testes e na validacao.",
            "A validacao reduziu erro e melhorou a consistencia dos modulos.",
            "O codigo ficou facil de manter, mas alguns testes poderiam ser ampliados.",
        ],
    },
    {
        "termos": ["preco", "orcamento", "custo", "valor", "investimento", "proposta", "pagamento", "budget"],
        "modelos": [
            "O preco ficou coerente com o escopo, o valor entregue e o investimento.",
            "O orcamento detalhado facilitou a negociacao da proposta e do pagamento.",
            "O custo-beneficio foi bom para o budget disponivel.",
        ],
    },
    {
        "termos": ["suporte", "posentrega", "duvida", "correcao", "treinamento", "manual", "uso", "ajuste"],
        "modelos": [
            "O suporte posentrega respondeu duvidas de uso com boa orientacao.",
            "As correcoes e ajustes foram tratados dentro do periodo de garantia.",
            "O treinamento e o manual facilitaram o uso da solucao depois da entrega.",
        ],
    },
    {
        "termos": ["documentacao", "apresentacao", "relatorio", "slide", "material", "grafico", "resumo", "visual"],
        "modelos": [
            "A documentacao explicou o material, o relatorio e os arquivos entregues.",
            "A apresentacao usou slide, grafico e resumo para mostrar os resultados.",
            "O visual dos slides ajudou a organizar material, grafico e apresentacao.",
        ],
    },
]


OUTLIERS_ALEATORIOS = [
    "Biblioteca silenciosa catalogo antigo prateleira poeira.",
    "Jardim externo banco molhado chuva madrugada.",
    "Cantina lateral sanduiche queimado fila barulhenta.",
    "Portao secundario cadeado enferrujado vigilancia noturna.",
    "Quadra esportiva bola furada rede rasgada.",
    "Laboratorio quimica frasco vazio bancada manchada.",
    "Bicicletario pequeno corrente solta pneu murcho.",
    "Impressora corredor toner fraco papel amassado.",
    "Bebedouro quebrado copo descartavel torneira vazando.",
    "Bibliografia antiga livro sumido etiqueta rasurada.",
    "Armario metalico chave torta dobradica rangendo.",
    "Ventilador teto ruido constante poeira acumulada.",
    "Janela emperrada cortina rasgada claridade excessiva.",
    "Microfone palco chiado alto bateria fraca.",
    "Relogio parede atrasado ponteiro solto visor trincado.",
    "Escada lateral corrimao frouxo degrau escorregadio.",
    "Mapa predio placa confusa rota bloqueada.",
    "Projetor reserva cabo curto entrada danificada.",
    "Recepcao vazia campainha baixa cracha esquecido.",
    "Lixeira seletiva adesivo apagado tampa quebrada.",
    "Arquivo morto caixa umida etiqueta perdida.",
    "Uniforme evento tamanho errado tecido arranhando.",
    "Chaveiro portaria codigo trocado gaveta travada.",
    "Balcao secretaria carimbo seco protocolo perdido.",
    "Cortador papel lamina cega regua solta.",
    "Cadeira auditorio espuma rasgada encosto torto.",
    "Persiana vertical trilho preso cordao rompido.",
    "Extintor corredor lacre vencido suporte solto.",
    "Tombo placa acrilico canto quebrado parafuso perdido.",
    "Mural avisos fita velha cartaz caido.",
    "Controle remoto pilha vazia botao afundado.",
    "Caixa som volume irregular conector oxidado.",
    "Tapete entrada borda levantada limpeza atrasada.",
    "Porta vidro adesivo torto puxador frouxo.",
    "Agenda recepcao pagina faltando caneta seca.",
    "Scanner antigo tampa desalinhada cabo gasto.",
    "Mesa dobravel perna bamba superficie riscada.",
    "Canaleta eletrica aberta fio exposto parede.",
    "Arquivo digital pasta duplicada nome confuso.",
    "Etiqueta patrimonio numero borrado cola fraca.",
]


def gerar_feedbacks_aleatorios(total: int = 90) -> list[str]:
    feedbacks = []
    quantidade_outliers = max(1, round(total * 0.08)) if total >= 20 else 0
    quantidade_tematicos = total - quantidade_outliers

    while len(feedbacks) < quantidade_tematicos:
        for topico in TOPICOS_ALEATORIOS:
            if len(feedbacks) >= quantidade_tematicos:
                break
            indice = len(feedbacks)
            termos = topico["termos"]
            modelo = topico["modelos"][indice % len(topico["modelos"])]
            a = termos[indice % len(termos)]
            b = termos[(indice + 2) % len(termos)]
            c = termos[(indice + 4) % len(termos)]
            feedbacks.append(f"{modelo} {a} {b} {c}.")

    for indice in range(quantidade_outliers):
        feedbacks.append(OUTLIERS_ALEATORIOS[indice % len(OUTLIERS_ALEATORIOS)])

    return feedbacks


def limpar_feedbacks_texto(conteudo: str) -> list[str]:
    linhas = [linha.strip() for linha in conteudo.splitlines() if linha.strip()]
    if linhas and linhas[0].lower() == "feedback":
        return linhas[1:]
    return linhas


def analisar_feedbacks(feedbacks: list[str]) -> dict:
    if not feedbacks:
        raise ValueError("Envie ao menos um feedback para analise.")

    with redirect_stdout(StringIO()):
        conjuntos_lemas, freq_global = preprocess_feedbacks(feedbacks)
        conjuntos_por_id = {indice: conjunto for indice, conjunto in enumerate(conjuntos_lemas)}
        matriz = construir_matriz_adjacencia(conjuntos_lemas)
        graus = calcular_graus(matriz)
        grau_medio = calcular_grau_medio(graus)
        densidade = calcular_densidade(matriz)
        grafo_relevante = _montar_grafo_relevante(matriz)
        arvore = prim_maximum_spanning_tree(matriz)
        resultado_comunidades = detect_communities(arvore, matriz)
        comunidades = resultado_comunidades["communities"]
        outliers = resultado_comunidades["outliers"]
        grafo_final = resultado_comunidades["final_graph"]
        topicos = nomear_topicos(comunidades, conjuntos_por_id)

    triangulos = detectar_triangulos(grafo_relevante)
    relatorio = _montar_relatorio(
        feedbacks,
        conjuntos_lemas,
        freq_global,
        matriz,
        grau_medio,
        densidade,
        arvore,
        comunidades,
        outliers,
        resultado_comunidades,
        topicos,
        triangulos,
    )
    visualizacoes = gerar_visualizacoes(
        feedbacks,
        grafo_relevante,
        comunidades,
        outliers,
        grafo_final,
        topicos,
    )

    return {
        "metricas": {
            "feedbacks": len(feedbacks),
            "lemas_unicos": len(freq_global),
            "matriz": f"{len(matriz)} x {len(matriz)}",
            "grau_medio": round(grau_medio, 2),
            "densidade": round(densidade, 4),
            "arestas_agm": len(arvore),
            "comunidades": len(comunidades),
            "outliers": len(outliers),
            "triangulos": len(triangulos),
        },
        "relatorio": relatorio,
        "topicos": _serializar_topicos(topicos, len(feedbacks)),
        "visualizacoes": visualizacoes,
    }


def _montar_grafo_relevante(matriz, limiar=LIMIAR_RELEVANCIA):
    grafo = {vertice: [] for vertice in range(len(matriz))}
    for i in range(len(matriz)):
        for j in range(i + 1, len(matriz)):
            if matriz[i][j] >= limiar:
                grafo[i].append(j)
                grafo[j].append(i)
    return grafo


def _montar_relatorio(
    feedbacks,
    conjuntos_lemas,
    freq_global,
    matriz,
    grau_medio,
    densidade,
    arvore,
    comunidades,
    outliers,
    resultado_comunidades,
    topicos,
    triangulos,
):
    linhas = [
        "TopicGraph EJ - Relatorio de analise",
        "=" * 44,
        f"Feedbacks analisados: {len(feedbacks)}",
        f"Conjuntos de lemas gerados: {len(conjuntos_lemas)}",
        f"Lemas unicos encontrados: {len(freq_global)}",
        f"Matriz de adjacencia: {len(matriz)} x {len(matriz)}",
        f"Grau medio inicial: {grau_medio:.2f}",
        f"Densidade inicial: {densidade:.4f}",
        f"Arestas na AGM maxima: {len(arvore)}",
        f"Arestas fracas removidas: {len(resultado_comunidades['removed_edges'])}",
        f"Comunidades detectadas: {len(comunidades)}",
        f"Outliers detectados: {len(outliers)}",
        f"Triangulos/Cliques K3 no grafo filtrado: {len(triangulos)}",
        "",
        "Topicos detectados",
        "-" * 44,
    ]

    for nome_topico, dados in topicos.items():
        tamanho = len(dados["feedbacks_ids"])
        percentual = (tamanho / len(feedbacks)) * 100 if feedbacks else 0
        palavras = ", ".join(dados["palavras_chave"])
        linhas.append(f"{nome_topico} - {dados['nome_automatico']}")
        linhas.append(f"  Palavras-chave: {palavras}")
        linhas.append(f"  Tamanho: {tamanho} feedbacks ({percentual:.2f}%)")

    if outliers:
        linhas.append("")
        linhas.append(f"Outliers: {outliers}")

    return "\n".join(linhas)


def _serializar_topicos(topicos, total_feedbacks):
    dados = []
    for nome, topico in topicos.items():
        tamanho = len(topico["feedbacks_ids"])
        dados.append(
            {
                "id": nome,
                "nome": topico["nome_automatico"],
                "palavras_chave": topico["palavras_chave"],
                "feedbacks": tamanho,
                "percentual": round((tamanho / total_feedbacks) * 100, 2),
            }
        )
    return dados


def gerar_visualizacoes(feedbacks, grafo_relevante, comunidades, outliers, grafo_final, topicos):
    inicial = _svg_vertices_iniciais(feedbacks)
    filtrado = _svg_grafo(grafo_relevante, "2. Grafo de similaridades filtrado", dfs_components(grafo_relevante))
    comunidades_svg = _svg_comunidades(comunidades, outliers, grafo_final, topicos)
    fluxo = _svg_fluxo_triplo(inicial, filtrado, comunidades_svg)
    return {
        "vertices_iniciais": inicial,
        "grafo_filtrado": filtrado,
        "comunidades": comunidades_svg,
        "fluxo_completo": fluxo,
    }


def _svg_base(titulo, subtitulo, corpo, largura=880, altura=560):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}">
<rect width="100%" height="100%" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-family="Segoe UI, Arial" font-size="21" font-weight="700" fill="#0f172a">{escape(titulo)}</text>
<text x="28" y="64" font-family="Segoe UI, Arial" font-size="13" fill="#475569">{escape(subtitulo)}</text>
{corpo}
</svg>"""


def _svg_vertices_iniciais(feedbacks):
    largura, altura = 880, 560
    cx, cy = largura / 2, altura / 2 + 24
    nos = []
    for i, feedback in enumerate(feedbacks):
        angulo = i * 2.399963229728653
        raio = 12 * sqrt(i)
        x = cx + raio * cos(angulo)
        y = cy + raio * sin(angulo)
        cor = "#0f766e" if i % 2 == 0 else "#2563eb"
        nos.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.7" fill="{cor}" stroke="#0f172a" stroke-width="0.6">'
            f"<title>Feedback {i}: {escape(feedback[:120])}</title></circle>"
        )
    return _svg_base(
        "1. Vertices iniciais",
        f"{len(feedbacks)} feedbacks isolados, antes do calculo de similaridade",
        "".join(nos),
        largura,
        altura,
    )


def _posicoes_grupos(grupos, largura=880, altura=560):
    cx, cy = largura / 2, altura / 2
    raio_principal = min(largura, altura) * 0.33
    posicoes, cores, rotulos = {}, {}, {}

    for indice, grupo in enumerate(grupos):
        angulo = 2 * pi * indice / max(len(grupos), 1)
        gcx = cx + raio_principal * cos(angulo)
        gcy = cy + raio_principal * sin(angulo)
        raio_local = max(28, min(78, 18 + len(grupo) * 2.6))
        cor = PALETA[indice % len(PALETA)]
        for j, vertice in enumerate(grupo):
            local = 2 * pi * j / max(len(grupo), 1)
            anel = raio_local * (0.55 + 0.45 * ((j % 4) + 1) / 4)
            posicoes[vertice] = (gcx + anel * cos(local), gcy + anel * sin(local))
            cores[vertice] = cor
            rotulos[vertice] = indice + 1

    return posicoes, cores, rotulos


def _svg_grafo(grafo, titulo, grupos):
    largura, altura = 880, 560
    grupos = sorted([sorted(grupo) for grupo in grupos], key=len, reverse=True)
    posicoes, cores, rotulos = _posicoes_grupos(grupos, largura, altura)
    arestas = []
    for origem, vizinhos in grafo.items():
        for destino in vizinhos:
            if origem < destino:
                x1, y1 = posicoes[origem]
                x2, y2 = posicoes[destino]
                arestas.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    'stroke="#94a3b8" stroke-width="0.8" opacity="0.32"/>'
                )
    nos = []
    for vertice, (x, y) in posicoes.items():
        nos.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.1" fill="{cores[vertice]}" stroke="#0f172a" stroke-width="0.6">'
            f"<title>Feedback {vertice} | grupo visual {rotulos[vertice]} | grau {len(grafo[vertice])}</title></circle>"
        )
    subtitulo = f"{len(grafo)} vertices, {len(arestas)} arestas relevantes, {len(grupos)} componentes visuais"
    return _svg_base(titulo, subtitulo, "".join(arestas + nos), largura, altura)


def _svg_comunidades(comunidades, outliers, grafo_final, topicos):
    largura, altura = 880, 560
    grupos = [sorted(grupo) for grupo in comunidades]
    if outliers:
        grupos.append(sorted(outliers))
    posicoes, cores, rotulos = _posicoes_grupos(grupos, largura, altura)
    arestas = []
    for origem, vizinhos in grafo_final.items():
        for destino in vizinhos:
            if origem < destino and origem in posicoes and destino in posicoes:
                x1, y1 = posicoes[origem]
                x2, y2 = posicoes[destino]
                arestas.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    'stroke="#334155" stroke-width="1.1" opacity="0.34"/>'
                )
    nos = []
    for vertice, (x, y) in posicoes.items():
        nos.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{cores[vertice]}" stroke="#0f172a" stroke-width="0.7">'
            f"<title>Feedback {vertice} | comunidade {rotulos[vertice]}</title></circle>"
        )

    legenda = []
    y = 92
    for indice, (chave, dados) in enumerate(topicos.items()):
        cor = PALETA[indice % len(PALETA)]
        legenda.append(f'<rect x="28" y="{y - 10}" width="10" height="10" rx="2" fill="{cor}"/>')
        legenda.append(
            f'<text x="44" y="{y}" font-family="Segoe UI, Arial" font-size="11" fill="#334155">'
            f"{escape(chave)}: {escape(dados['nome_automatico'])}</text>"
        )
        y += 16

    subtitulo = f"{len(comunidades)} comunidades detectadas, {len(outliers)} outliers"
    return _svg_base("3. Comunidades detectadas", subtitulo, "".join(arestas + nos + legenda), largura, altura)


def _svg_fluxo_triplo(inicial, filtrado, comunidades):
    largura, altura = 2760, 640
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}">
<rect width="100%" height="100%" fill="#e2e8f0"/>
<g transform="translate(24 40)">{_svg_interno(inicial)}</g>
<text x="914" y="330" font-family="Segoe UI, Arial" font-size="34" font-weight="700" fill="#0f172a">→</text>
<g transform="translate(946 40)">{_svg_interno(filtrado)}</g>
<text x="1836" y="330" font-family="Segoe UI, Arial" font-size="34" font-weight="700" fill="#0f172a">→</text>
<g transform="translate(1868 40)">{_svg_interno(comunidades)}</g>
</svg>"""


def _svg_interno(svg):
    inicio = svg.find(">") + 1
    fim = svg.rfind("</svg>")
    return svg[inicio:fim]
