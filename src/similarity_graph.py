# Similaridade de Jaccard: divide a quantidade de lemas em comum pela quantidade total de 
# lemas diferentes nos dois conjuntos.

def jaccard(a, b):
    if len(a) == 0 and len(b) == 0:
        return 0

    intersecao = 0
    for item in a:
        if item in b:
            intersecao += 1

    uniao = len(a) + len(b) - intersecao

    return intersecao / uniao

# Constroi a matriz comparando cada par de feedbacks com Jaccard e salvando o peso da relacao nas 
# posicoes simetricas.
def construir_matriz_adjacencia(conjuntos_lemas):
    n = len(conjuntos_lemas)

    matriz = []
    for i in range (n):
        linha = []
        for j in range(n):
            linha.append(0)
        matriz.append(linha)

    for i in range (n):
        for j in range(i + 1, n):
            peso = jaccard(conjuntos_lemas[i], conjuntos_lemas[j])
            matriz[i][j] = peso
            matriz[j][i] = peso

    return matriz

