import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis import (
    HashTable, 
    extrair_palavras_frequentes, 
    nomear_topicos, 
    detectar_triangulos,
    calcular_metricas_finais
)


def test_hash_table_operacoes():
    print("🧪 Testando Issue #14: HashTable Manual...")
    tabela = HashTable(tamanho_inicial=3)
    tabela.incrementar("prazo")
    tabela.incrementar("prazo")
    tabela.incrementar("suporte")
    
    itens = dict(tabela.itens())
    
    assert itens["prazo"] == 2, "Erro: A frequência de 'prazo' deveria ser 2."
    assert itens["suporte"] == 1, "Erro: A frequência de 'suporte' deveria ser 1."
    print("   -> HashTable: OK (Inserção, Incremento e Colisões tratadas).")


def test_extrair_palavras_frequentes():
    print("🧪 Testando Issue #15: Extração de Palavras Frequentes...")
    
    conjuntos_lemas = {
        10: {"atrasar", "entrega", "prazo"},
        11: {"atrasar", "logistica"},
        12: {"preco", "caro"}
    }
    comunidade = [10, 11]
    
    top_termos = extrair_palavras_frequentes(comunidade, conjuntos_lemas, top_k=2)   
    assert top_termos[0][0] == "atrasar", "Erro: 'atrasar' deveria ser o termo mais frequente."
    assert top_termos[0][1] == 2, "Erro: A frequência de 'atrasar' deveria ser 2."
    assert len(top_termos) == 2, "Erro: O retorno deveria conter exatamente o top_k solicitado."
    print("   -> Extração de Termos: OK (Ordenação e limite top_k respeitados).")


def test_nomear_topicos_e_outliers():
    print("🧪 Testando Issue #16: Nomeação de Tópicos e Tratamento de Outliers...")
    
    conjuntos_lemas = {
        0: {"suporte", "atendimento", "demorar"},
        1: {"suporte", "ajuda"}
    }
    comunidades = [[0, 1], []]
    
    resultado = nomear_topicos(comunidades, conjuntos_lemas)

# Valida se mapeou corretamente as chaves dos tópicos
    assert "Tópico_1" in resultado, "Erro: A chave 'Tópico_1' deveria existir no resultado."
    assert "Tópico_2" in resultado, "Erro: A chave 'Tópico_2' deveria existir no resultado."
    
    # Valida se guardou os IDs dos feedbacks corretamente
    assert resultado["Tópico_1"]["feedbacks_ids"] == [0, 1]
    
    # Valida se extraiu a palavra-chave correta
    assert "suporte" in resultado["Tópico_1"]["palavras_chave"]
    
    # Valida o novo rótulo de segurança para tópicos vazios conforme a regra de negócio atualizada
    assert resultado["Tópico_2"]["palavras_chave"] == "Tópico não classificado", "Erro: Deveria rotular adequadamente uma comunidade vazia."
    print("   -> Nomeação de Tópicos: OK.")


def test_detectar_triangulos_e_metricas(capsys):
    print("🧪 Testando Issue #17: Triângulos e Resumo Estatístico do Grafo...")
    
    # Simula uma lista de adjacências contendo um triângulo perfeito entre os nós 1, 2 e 3
    adj_list = {
        1: [2, 3],
        2: [1, 3],
        3: [1, 2],
        4: []  # Nó isolado (outlier)
    }
    
    # 1. Testa a função matemática de detecção de cliques K3
    triangulos = detectar_triangulos(adj_list)
    assert len(triangulos) == 1, "Erro: Deveria ter detectado exatamente 1 triângulo."
    assert triangulos[0] == (1, 2, 3), "Erro: O triângulo detectado deveria ser (1, 2, 3)."
    
    # 2. Testa a exibição das métricas consolidadas com dados do Integrante 2
    comunidades = [[1, 2, 3], [4]] # Comunidade 2 possui tamanho 1 (outlier)
    dicionario_topicos = {
        "Tópico_1": {"feedbacks_ids": [1, 2, 3], "palavras_chave": "atraso, prazo"},
        "Tópico_2": {"feedbacks_ids": [4], "palavras_chave": "Tópico não classificado"}
    }
    
    # Executa passando dados simulados (densidade, grau médio e limiar)
    calcular_metricas_finais(
        comunidades=comunidades,
        dicionario_topicos=dicionario_topicos,
        total_feedbacks=4,
        densidade=0.5,
        grau_medio=2.0,
        limiar=0.25,
        adj_list=adj_list
    )
    
    saida = capsys.readouterr().out
    assert "Número total de comunidades: 2" in saida
    assert "Densidade calculada do grafo: 0.5000" in saida
    assert "Grau médio do grafo: 2.00" in saida
    assert "Limiar de arestas relevantes utilizado: 0.25" in saida
    assert "Triângulos/Cliques K3 detetados: 1" in saida
    assert "Quantidade de Outliers listados: 1" in saida
    print("   -> Métricas estruturais e relatório: OK.")


if __name__ == "__main__":
    print("====== INICIANDO SUÍTE DE TESTES Do Integrante 5(Interpretação e análise) ======\n") 
    test_hash_table_operacoes()
    test_extrair_palavras_frequentes()
    test_nomear_topicos_e_outliers()

    class CapsysMock:
        def readouterr(self):
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                calcular_metricas_finais([[1,2,3],[4]], {"T1":{"feedbacks_ids":[1,2,3],"palavras_chave":""}}, 4, 0.5, 2.0, 0.25, {1:[2,3],2:[1,3],3:[1,2],4:[]})
            return type('Output', (object,), {'out': f.getvalue()})()
            
    test_detectar_triangulos_e_metricas(CapsysMock())
    
    print("\n======================================================")
    print("🎉 PARABÉNS! Todas as suas issues foram validadas com 100% de sucesso!")
    print("======================================================")