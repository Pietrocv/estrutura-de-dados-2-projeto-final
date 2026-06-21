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