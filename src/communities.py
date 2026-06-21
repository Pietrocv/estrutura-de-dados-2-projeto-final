"""Modulo do integrante 4: corte de arestas e comunidades.

Este modulo recebe a arvore geradora maxima produzida pelo integrante 3 e a
matriz original de similaridade produzida pelo integrante 2. A partir disso,
remove ligacoes fracas, encontra componentes conexos por DFS/BFS e trata
vertices unitarios como anexacoes ou outliers.
"""

from collections import deque


LIMIAR_CORTE_PADRAO = 0.15
LIMIAR_ANEXACAO_PADRAO = 0.15


def _validar_matriz_quadrada(matriz):
    if not isinstance(matriz, list):
        raise TypeError("A matriz deve ser uma lista de listas.")

    n = len(matriz)
    for linha in matriz:
        if not isinstance(linha, list) or len(linha) != n:
            raise ValueError("A matriz deve ser quadrada.")


def _normalizar_aresta(aresta):
    if len(aresta) != 3:
        raise ValueError("Cada aresta deve ter o formato (origem, destino, peso).")

    origem, destino, peso = aresta
    return int(origem), int(destino), float(peso)


def criar_matriz_vazia(n_vertices):
    """Cria uma matriz n x n preenchida com zero."""
    if n_vertices < 0:
        raise ValueError("A quantidade de vertices nao pode ser negativa.")

    return [[0.0 for _ in range(n_vertices)] for _ in range(n_vertices)]


def construir_grafo_da_arvore(n_vertices, mst_edges):
    """Converte a lista de arestas da AGM em matriz de adjacencia ponderada."""
    grafo = criar_matriz_vazia(n_vertices)

    for aresta in mst_edges:
        origem, destino, peso = _normalizar_aresta(aresta)
        if origem < 0 or destino < 0 or origem >= n_vertices or destino >= n_vertices:
            raise ValueError("Aresta possui vertice fora do intervalo da matriz.")

        grafo[origem][destino] = peso
        grafo[destino][origem] = peso

    return grafo


def remover_arestas_fracas(
    mst_edges,
    n_vertices,
    limiar_corte=LIMIAR_CORTE_PADRAO,
    quantidade_cortes=None,
):
    """Remove arestas fracas da arvore.

    Por padrao, remove toda aresta com peso menor que ``limiar_corte``. Quando
    ``quantidade_cortes`` e informada, remove exatamente as K menores arestas,
    alternativa de teste prevista no documento tecnico.
    """
    arestas = [_normalizar_aresta(aresta) for aresta in mst_edges]
    arestas_ordenadas = sorted(arestas, key=lambda item: item[2])

    if quantidade_cortes is not None:
        if quantidade_cortes < 0:
            raise ValueError("A quantidade de cortes nao pode ser negativa.")
        selecionadas_para_remocao = arestas_ordenadas[:quantidade_cortes]
        removidas_set = set(selecionadas_para_remocao)
    else:
        selecionadas_para_remocao = [
            aresta for aresta in arestas_ordenadas if aresta[2] < limiar_corte
        ]
        removidas_set = set(selecionadas_para_remocao)

    grafo_final = criar_matriz_vazia(n_vertices)
    for origem, destino, peso in arestas:
        if (origem, destino, peso) in removidas_set:
            continue
        grafo_final[origem][destino] = peso
        grafo_final[destino][origem] = peso

    return grafo_final, selecionadas_para_remocao


def vizinhos_do_vertice(grafo, vertice):
    """Retorna os vizinhos conectados por arestas com peso maior que zero."""
    return [
        indice
        for indice, peso in enumerate(grafo[vertice])
        if indice != vertice and peso > 0
    ]


def dfs_componentes(grafo_final):
    """Encontra componentes conexos usando DFS iterativo."""
    _validar_matriz_quadrada(grafo_final)

    visitados = set()
    comunidades = []

    for vertice in range(len(grafo_final)):
        if vertice in visitados:
            continue

        componente = []
        pilha = [vertice]
        visitados.add(vertice)

        while pilha:
            atual = pilha.pop()
            componente.append(atual)

            for vizinho in vizinhos_do_vertice(grafo_final, atual):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    pilha.append(vizinho)

        comunidades.append(sorted(componente))

    return comunidades


def bfs_componentes(grafo_final):
    """Encontra componentes conexos usando BFS, util para validacao."""
    _validar_matriz_quadrada(grafo_final)

    visitados = set()
    comunidades = []

    for vertice in range(len(grafo_final)):
        if vertice in visitados:
            continue

        componente = []
        fila = deque([vertice])
        visitados.add(vertice)

        while fila:
            atual = fila.popleft()
            componente.append(atual)

            for vizinho in vizinhos_do_vertice(grafo_final, atual):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)

        comunidades.append(sorted(componente))

    return comunidades


def _melhor_comunidade_para_vertice(vertice, comunidades, matriz_original):
    melhor_indice = None
    melhor_vertice = None
    melhor_peso = 0.0

    for indice, comunidade in enumerate(comunidades):
        for candidato in comunidade:
            peso = float(matriz_original[vertice][candidato])
            if peso > melhor_peso:
                melhor_peso = peso
                melhor_indice = indice
                melhor_vertice = candidato

    return melhor_indice, melhor_vertice, melhor_peso


def tratar_vertices_unitarios(
    comunidades,
    matriz_original,
    grafo_final,
    limiar_anexacao=LIMIAR_ANEXACAO_PADRAO,
):
    """Anexa vertices unitarios ou classifica-os como outliers.

    Comunidades com dois ou mais vertices sao mantidas como comunidades
    principais. Cada comunidade unitaria e comparada com essas comunidades
    usando a matriz original de similaridade.
    """
    _validar_matriz_quadrada(matriz_original)
    _validar_matriz_quadrada(grafo_final)

    comunidades_principais = [list(c) for c in comunidades if len(c) > 1]
    vertices_unitarios = [c[0] for c in comunidades if len(c) == 1]
    outliers = []

    for vertice in vertices_unitarios:
        if not comunidades_principais:
            outliers.append(vertice)
            continue

        melhor_indice, melhor_vertice, melhor_peso = _melhor_comunidade_para_vertice(
            vertice, comunidades_principais, matriz_original
        )

        if melhor_peso >= limiar_anexacao:
            comunidades_principais[melhor_indice].append(vertice)
            grafo_final[vertice][melhor_vertice] = melhor_peso
            grafo_final[melhor_vertice][vertice] = melhor_peso
        else:
            outliers.append(vertice)

    comunidades_principais = [sorted(comunidade) for comunidade in comunidades_principais]
    comunidades_principais.sort(key=lambda comunidade: (comunidade[0], len(comunidade)))
    outliers.sort()

    return comunidades_principais, outliers, grafo_final


def detectar_comunidades(
    mst_edges,
    matriz_original,
    limiar_corte=LIMIAR_CORTE_PADRAO,
    limiar_anexacao=LIMIAR_ANEXACAO_PADRAO,
    quantidade_cortes=None,
):
    """Executa o fluxo completo do modulo do integrante 4.

    Retorna um dicionario com:
    - comunidades: grupos finais de IDs de feedbacks;
    - outliers: feedbacks que nao se encaixaram em nenhum grupo;
    - grafo_final: matriz da arvore apos cortes e anexacoes;
    - arestas_removidas: ligacoes fracas removidas da AGM;
    - comunidades_antes_do_tratamento: componentes logo apos o corte.
    """
    _validar_matriz_quadrada(matriz_original)
    n_vertices = len(matriz_original)

    grafo_cortado, arestas_removidas = remover_arestas_fracas(
        mst_edges,
        n_vertices,
        limiar_corte=limiar_corte,
        quantidade_cortes=quantidade_cortes,
    )
    comunidades_iniciais = dfs_componentes(grafo_cortado)
    comunidades, outliers, grafo_final = tratar_vertices_unitarios(
        comunidades_iniciais,
        matriz_original,
        grafo_cortado,
        limiar_anexacao=limiar_anexacao,
    )

    return {
        "comunidades": comunidades,
        "outliers": outliers,
        "grafo_final": grafo_final,
        "arestas_removidas": arestas_removidas,
        "comunidades_antes_do_tratamento": comunidades_iniciais,
    }
