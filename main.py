from pathlib import Path
import sys

from src.analysis import calcular_metricas_finais, nomear_topicos
from src.communities import detect_communities
from src.preprocessing import preprocess_feedbacks, read_feedbacks_txt
from src.prim_max import prim_maximum_spanning_tree
from src.similarity_graph import (
    LIMIAR_RELEVANCIA,
    calcular_densidade,
    calcular_grau_medio,
    calcular_graus,
    construir_matriz_adjacencia,
)


CAMINHO_FEEDBACKS = Path("data") / "feedbacks.txt"


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def remover_cabecalho_feedback(feedbacks):
    if feedbacks and feedbacks[0].strip().lower() == "feedback":
        return feedbacks[1:]

    return feedbacks


def imprimir_resumo_etapa(nome, valor):
    print(f"[OK] {nome}: {valor}")


def construir_grafo_relevante(matriz_adjacencia, limiar=LIMIAR_RELEVANCIA):
    grafo = {vertice: [] for vertice in range(len(matriz_adjacencia))}

    for i in range(len(matriz_adjacencia)):
        for j in range(i + 1, len(matriz_adjacencia)):
            if matriz_adjacencia[i][j] >= limiar:
                grafo[i].append(j)
                grafo[j].append(i)

    return grafo


def executar_pipeline(caminho_feedbacks=CAMINHO_FEEDBACKS):
    print("=" * 60)
    print("TopicGraph EJ - Pipeline completo")
    print("=" * 60)

    feedbacks = read_feedbacks_txt(str(caminho_feedbacks))
    feedbacks = remover_cabecalho_feedback(feedbacks)
    imprimir_resumo_etapa("Feedbacks lidos", len(feedbacks))

    conjuntos_lemas, freq_global = preprocess_feedbacks(feedbacks)
    conjuntos_por_id = {
        indice: conjunto
        for indice, conjunto in enumerate(conjuntos_lemas)
    }
    imprimir_resumo_etapa("Conjuntos de lemas gerados", len(conjuntos_lemas))
    imprimir_resumo_etapa("Lemas unicos encontrados", len(freq_global))

    matriz_adjacencia = construir_matriz_adjacencia(conjuntos_lemas)
    tamanho_matriz = len(matriz_adjacencia)
    imprimir_resumo_etapa(
        "Matriz de adjacencia criada",
        f"{tamanho_matriz} x {tamanho_matriz}",
    )

    graus = calcular_graus(matriz_adjacencia)
    grau_medio = calcular_grau_medio(graus)
    densidade = calcular_densidade(matriz_adjacencia)
    grafo_relevante = construir_grafo_relevante(matriz_adjacencia)
    imprimir_resumo_etapa("Grau medio inicial", f"{grau_medio:.2f}")
    imprimir_resumo_etapa("Densidade inicial", f"{densidade:.4f}")

    arvore_geradora_maxima = prim_maximum_spanning_tree(matriz_adjacencia)
    imprimir_resumo_etapa(
        "Arestas na arvore geradora maxima",
        len(arvore_geradora_maxima),
    )

    resultado_comunidades = detect_communities(
        arvore_geradora_maxima,
        matriz_adjacencia,
    )
    comunidades = resultado_comunidades["communities"]
    outliers = resultado_comunidades["outliers"]
    grafo_final = resultado_comunidades["final_graph"]
    imprimir_resumo_etapa("Comunidades detectadas", len(comunidades))
    imprimir_resumo_etapa("Outliers detectados", len(outliers))
    imprimir_resumo_etapa(
        "Arestas fracas removidas",
        len(resultado_comunidades["removed_edges"]),
    )

    comunidades_para_relatorio = comunidades + [[outlier] for outlier in outliers]
    topicos = nomear_topicos(comunidades_para_relatorio, conjuntos_por_id)

    calcular_metricas_finais(
        comunidades=comunidades_para_relatorio,
        dicionario_topicos=topicos,
        total_feedbacks=len(feedbacks),
        densidade=densidade,
        grau_medio=grau_medio,
        limiar=LIMIAR_RELEVANCIA,
        adj_list=grafo_relevante,
    )

    return {
        "feedbacks": feedbacks,
        "conjuntos_lemas": conjuntos_lemas,
        "freq_global": freq_global,
        "matriz_adjacencia": matriz_adjacencia,
        "graus": graus,
        "grau_medio": grau_medio,
        "densidade": densidade,
        "grafo_relevante": grafo_relevante,
        "arvore_geradora_maxima": arvore_geradora_maxima,
        "comunidades": comunidades,
        "outliers": outliers,
        "topicos": topicos,
    }


if __name__ == "__main__":
    executar_pipeline()
