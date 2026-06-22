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