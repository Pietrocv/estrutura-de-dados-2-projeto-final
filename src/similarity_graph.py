#Regra de negocio definnido pelo grupo, valor pode ser alterado a depender da execucao
LIMIAR_RELEVANCIA = 0.2

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

#Se o peso for maior ou igual ao limiar definido temos a conexao
def calcular_graus(matriz_pesos):
    graus = []

    for linha in matriz_pesos:
        grau = 0
        for peso in linha:
            if peso >= LIMIAR_RELEVANCIA:
                grau += 1
        graus.append(grau)

    return graus

#Soma todos os graus e divide pela quantiade de verticies
def calcular_grau_medio(graus):
    if len(graus) == 0:
        return 0

    soma = 0
    for grau in graus:
        soma += grau

    return soma / len(graus)

#Calcula a densidade, no caso esse e um grafo nao direcionado
def calcular_densidade(matriz_pesos):
    n = len(matriz_pesos)

    if n <= 1:
        return 0

    arestas = 0

    for i in range(n):
        for j in range(i + 1, n):
            if matriz_pesos[i][j] >= LIMIAR_RELEVANCIA:
                arestas += 1

    arestas_possiveis = n * (n - 1) / 2

    return arestas / arestas_possiveis    


