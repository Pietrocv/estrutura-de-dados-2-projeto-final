import math


class ElementoHash:
    def __init__(self, chave, valor):
        self.chave = chave
        self.valor = valor

class HashTable:
    def __init__(self, tamanho_inicial=37):
        self.tamanho = tamanho_inicial
        # Cria os buckets usando listas nativas para o encadeamento separado (tratamento de colisão)
        self.tabela = [[] for _ in range(self.tamanho)]

    def _funcao_hash(self, chave):
        soma_ascii = sum(ord(c) for c in str(chave))
        return soma_ascii % self.tamanho

    def incrementar(self, chave):
        indice = self._funcao_hash(chave)
        bucket = self.tabela[indice]
        
        for elemento in bucket:
            if elemento.chave == chave:
                elemento.valor += 1
                return
        
        # Caso a palavra não esteja no bucket, adiciona ela com valor 1
        bucket.append(ElementoHash(chave, 1))

    def itens(self):
        resultado = []
        for bucket in self.tabela:
            for elemento in bucket:
                resultado.append((elemento.chave, elemento.valor))
        return resultado
    
def extrair_palavras_frequentes(comunidade, conjuntos_lemas, top_k=5):
    # Conta a frequência dos lemas de uma comunidade usando a HashTable.
    tabela = HashTable()
    
    # Percorre cada ID de feedback pertencente à comunidade
    for id_feedback in comunidade:
        # Verifica se o ID do feedback existe no dicionário global de lemas
        if id_feedback in conjuntos_lemas:
            for lema in conjuntos_lemas[id_feedback]:
                tabela.incrementar(lema)
                
    # Obtém os pares armazenados na HashTable
    pares = tabela.itens()
    
    # Ordena os pares por frequência de forma decrescente
    pares_ordenados = sorted(pares, key=lambda x: x[1], reverse=True)
    
    # Retorna apenas a quantidade pedida
    return pares_ordenados[:top_k]

def _frequencias_da_comunidade(comunidade, conjuntos_lemas):
    tabela = HashTable()

    for id_feedback in comunidade:
        for lema in conjuntos_lemas.get(id_feedback, set()):
            tabela.incrementar(lema)

    return tabela.itens()


def _frequencia_entre_comunidades(comunidades, conjuntos_lemas):
    frequencia = {}

    for comunidade in comunidades:
        termos_da_comunidade = set()

        for id_feedback in comunidade:
            termos_da_comunidade.update(conjuntos_lemas.get(id_feedback, set()))

        for termo in termos_da_comunidade:
            frequencia[termo] = frequencia.get(termo, 0) + 1

    return frequencia


def extrair_termos_representativos(
    comunidade,
    conjuntos_lemas,
    frequencia_entre_comunidades,
    total_comunidades,
    top_k=3,
):
    """
    Seleciona termos frequentes dentro da comunidade e raros nas demais.
    """
    if top_k <= 0 or not comunidade:
        return []

    termos_pontuados = []

    for termo, frequencia_local in _frequencias_da_comunidade(
        comunidade,
        conjuntos_lemas,
    ):
        comunidades_com_termo = frequencia_entre_comunidades.get(termo, 0)
        raridade = math.log(
            (total_comunidades + 1) / (comunidades_com_termo + 1)
        ) + 1
        proporcao_local = frequencia_local / len(comunidade)

        termos_pontuados.append(
            {
                "termo": termo,
                "frequencia": frequencia_local,
                "pontuacao": proporcao_local * raridade,
            }
        )

    termos_pontuados.sort(
        key=lambda item: (
            -item["pontuacao"],
            -item["frequencia"],
            item["termo"],
        )
    )

    return termos_pontuados[:top_k]


def _formatar_nome_topico(termos_representativos):
    if not termos_representativos:
        return "Tópico não classificado"

    termos = [item["termo"].capitalize() for item in termos_representativos]
    return " / ".join(termos)


def nomear_topicos(comunidades, conjuntos_lemas, top_k=3):
    """
    Nomeia comunidades já detectadas sem interferir na formação dos grupos.

    O nome é produzido diretamente a partir dos lemas mais representativos,
    sem catálogo prévio de assuntos.
    """
    dicionario_topicos = {}
    frequencia_global = _frequencia_entre_comunidades(
        comunidades,
        conjuntos_lemas,
    )
    total_comunidades = len(comunidades)

    for i, comunidade in enumerate(comunidades):
        termos_representativos = extrair_termos_representativos(
            comunidade,
            conjuntos_lemas,
            frequencia_global,
            total_comunidades,
            top_k=top_k,
        )

        dicionario_topicos[f"Tópico_{i+1}"] = {
            "feedbacks_ids": comunidade,
            "nome_automatico": _formatar_nome_topico(
                termos_representativos
            ),
            "palavras_chave": [
                item["termo"] for item in termos_representativos
            ],
            "termos_representativos": termos_representativos,
        }

    return dicionario_topicos

def detectar_triangulos(adj_list):
    triangulos = set()
    vertices = list(adj_list.keys())
    
    for u in vertices:
        for v in adj_list[u]:
            if v > u:  # Evita duplicar caminhos no grafo não direcionado
                for w in adj_list[v]:
                    if w > v and w in adj_list[u]:
                        triangulos.add(tuple(sorted([u, v, w])))
    return list(triangulos)

def calcular_metricas_finais(comunidades, dicionario_topicos, total_feedbacks, densidade, grau_medio, limiar, adj_list, outliers=None):
    if outliers is None:
        outliers = []

    triangulos = detectar_triangulos(adj_list)
    
    print("\n" + "="*50)
    print("RELATÓRIO FINAL E RESUMO ESTATÍSTICO DO GRAFO")
    print("="*50)
    print(f"Número total de comunidades: {len(comunidades)}")
    print(f"Densidade calculada do grafo: {densidade:.4f}")
    print(f"Grau médio do grafo: {grau_medio:.2f}")
    print(f"Limiar de arestas relevantes utilizado: {limiar}")
    print(f"Triângulos/Cliques K3 detetados: {len(triangulos)}")
    print(f"Quantidade de Outliers listados: {len(outliers)} (IDs: {outliers})")
    print("-" * 50)
    
    for nome_topico, dados in dicionario_topicos.items():
        qtd_feedbacks = len(dados["feedbacks_ids"])
        # Calcula a porcentagem de representatividade do tópico (Tamanho de cada comunidade)
        porcentagem = (qtd_feedbacks / total_feedbacks) * 100 if total_feedbacks > 0 else 0
        
        print(f"\n{nome_topico} — {dados['nome_automatico']}")
        print(
            "   -> Palavras-chave: "
            + ", ".join(dados["palavras_chave"])
        )
        print(f"   -> Tamanho da comunidade: {qtd_feedbacks} feedbacks")
        print(f"   -> Representa {porcentagem:.2f}% do total analisado.")
