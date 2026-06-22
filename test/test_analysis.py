import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis import HashTable, extrair_palavras_frequentes, nomear_topicos, calcular_metricas_finais


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

    assert "Topico_1" in resultado
    assert resultado["Topico_1"]["feedbacks_ids"] == [0, 1]
    assert "suporte" in resultado["Topico_1"]["palavras_chave"]
    assert resultado["Topico_2"]["palavras_chave"] == "Sem termos relevantes", "Erro: Deveria rotular adequadamente uma comunidade vazia."
    print("   -> Nomeação de Tópicos: OK (Estrutura de dicionário, IDs guardados e tratamento de outliers).")


def test_calcular_metricas_finais(capsys):
    print("🧪 Testando Issue #17: Exibição de Métricas Finais...")
    
    dicionario_topicos = {
        "Topico_1": {"feedbacks_ids": [1, 2, 3], "palavras_chave": "atraso, entrega"},
        "Topico_2": {"feedbacks_ids": [4], "palavras_chave": "preco"}
    }
    total_feedbacks = 4
    
    calcular_metricas_finais(dicionario_topicos, total_feedbacks)

    saida = capsys.readouterr().out
    
    assert "Quantidade de feedbacks: 3" in saida
    assert "Representa 75.00%" in saida
    assert "Representa 25.00%" in saida
    print("   -> Métricas de Negócio: OK (Cálculos de volumetria e percentuais exatos).")


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
                calcular_metricas_finais({
                    "Topico_1": {"feedbacks_ids": [1, 2, 3], "palavras_chave": "atraso, entrega"},
                    "Topico_2": {"feedbacks_ids": [4], "palavras_chave": "preco"}
                }, total_feedbacks=4)
            return type('Output', (object,), {'out': f.getvalue()})()
            
    test_calcular_metricas_finais(CapsysMock())
    
    print("\n======================================================")
    print("🎉 PARABÉNS! Todas as suas issues foram validadas com 100% de sucesso!")
    print("======================================================")