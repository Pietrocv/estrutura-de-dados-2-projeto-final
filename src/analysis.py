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

def nomear_topicos(comunidades, conjuntos_lemas):
    # Mapeia cada comunidade para um dicionário contendo os IDs dos feedbacks e uma string com as palavras-chave mais frequentes que dão nome ao tópico.
    dicionario_topicos = {}
    
    for i, comunidade in enumerate(comunidades):
        # Pega as 3 palavras mais frequentes para dar nome ao tópico (top_k=3)
        top_termos = extrair_palavras_frequentes(comunidade, conjuntos_lemas, top_k=3)
        
        # Junta os termos com uma vírgula. Ex: "atrasar, entrega, prazo"
        nome_topico = ", ".join([termo[0] for termo in top_termos])
        
        # Guarda a estrutura de dados da comunidade rotulada
        dicionario_topicos[f"Tópico_{i+1}"] = {
            "feedbacks_ids": comunidade,
            "palavras_chave": nome_topico if nome_topico else "Tópico não classificado"
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

def calcular_metricas_finais(comunidades, dicionario_topicos, total_feedbacks, densidade, grau_medio, limiar, adj_list):
    # Identifica os outliers (comunidades de tamanho igual a 1)
    outliers = [c[0] for c in comunidades if len(c) == 1]
    triangulos = detectar_triangulos(adj_list)
    
    print("\n" + "="*50)
    print("RELATÓRIO FINAL E RESUMO ESTATÍSTICO DO GRAFO")
    print("="*50)
    print(f"👉 Número total de comunidades: {len(comunidades)}")
    print(f"👉 Densidade calculada do grafo: {densidade:.4f}")
    print(f"👉 Grau médio do grafo: {grau_medio:.2f}")
    print(f"👉 Limiar de arestas relevantes utilizado: {limiar}")
    print(f"👉 Triângulos/Cliques K3 detetados: {len(triangulos)}")
    print(f"👉 Quantidade de Outliers listados: {len(outliers)} (IDs: {outliers})")
    print("-" * 50)
    
    for nome_topico, dados in dicionario_topicos.items():
        qtd_feedbacks = len(dados["feedbacks_ids"])
        # Calcula a porcentagem de representatividade do tópico (Tamanho de cada comunidade)
        porcentagem = (qtd_feedbacks / total_feedbacks) * 100 if total_feedbacks > 0 else 0
        
        print(f"\n📌 {nome_topico}: [{dados['palavras_chave']}]")
        print(f"   -> Tamanho da comunidade: {qtd_feedbacks} feedbacks")
        print(f"   -> Representa {porcentagem:.2f}% do total analisado.")