import unicodedata
import string       
import spacy        

# Carregamento do modelo spaCy para português. O modelo "pt_core_news_sm"
try:
    _NLP = spacy.load("pt_core_news_sm")
except OSError:
    raise OSError(
        "[preprocessing.py] Modelo spaCy 'pt_core_news_sm' não encontrado.\n"
        "Execute: python -m spacy download pt_core_news_sm"
    )


# Carregamento dos feedbacks
def read_feedbacks_txt(path: str) -> list[str]:
# Lê o arquivo de feedbacks e retorna uma lista de strings
    feedbacks: list[str] = []

    try:
        with open(path, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                texto = linha.strip() # strip() remove espaços em branco e quebras de linha (\n) das bordas

                if texto:
                    feedbacks.append(texto)

    except FileNotFoundError:
        raise FileNotFoundError(
            f"[read_feedbacks_txt] Arquivo não encontrado: '{path}'\n"
            "Verifique se o arquivo 'feedbacks.txt' está em 'data/'."
        )

    # Validação extra
    if not feedbacks:
        raise ValueError(
            f"[read_feedbacks_txt] O arquivo '{path}' não contém "
            "nenhum feedback válido (todas as linhas estão vazias)."
        )

    return feedbacks


# Funções auxiliares internas
def _remove_accents(text: str) -> str:
    # Passo 1: Decompõe caracteres acentuados em letra + marca de acento
    normalizado = unicodedata.normalize("NFD", text)

    # Passo 2: Filtra os caracteres, mantendo apenas aqueles que NÃO são
    # marcas de combinação (categoria Unicode "Mn" = Mark, Nonspacing).
    # A função unicodedata.category(char) retorna a categoria do caractere.
    return "".join(
        char for char in normalizado
        if unicodedata.category(char) != "Mn"
    )


def _remove_punctuation(text: str) -> str:
    # str.maketrans cria uma tabela de tradução que mapeia cada caractere
    # de pontuação para None (deleção). str.translate aplica essa tabela
    # eficientemente em toda a string de uma só vez
    tabela_remocao = str.maketrans("", "", string.punctuation)
    return text.translate(tabela_remocao)


def _increment_freq(
    freq_table: dict[str, int],
    lema: str
) -> dict[str, int]:
    # dict.get(chave, valor_padrao) retorna o valor atual se a chave
    # existir, ou 0 se for a primeira ocorrência. Somamos 1 para incrementar.
    freq_table[lema] = freq_table.get(lema, 0) + 1
    return freq_table


# Pré-processamento e geração dos conjuntos de lemas
def _preprocess_single_feedback(feedback: str) -> set[str]:
    # Lowercase (normaliza as maiúsculas)
    texto = feedback.lower()

    # Remoção de pontuação (remove vírgulas, pontos, aspas etc. antes de entrar no spaCy)
    texto = _remove_punctuation(texto)

    # Tokenização com spaCy (_NLP(texto) executa o pipeline completo do spaCy e retorna um doc com tokens e atributos)
    doc = _NLP(texto)

    conjunto_lemas: set[str] = set()

    for token in doc:
        # Filtro de stopwords
        if token.is_stop:
            continue

        # Filtro de espaços
        if token.is_space:
            continue

        # Filtro de pontuação residual (alguns tokens podem ser pontuação mesmo após _remove_punctuation, como hífens em palavras compostas)
        if token.is_punct:
            continue

        # Filtro de tokens que são só dígitos
        if token.is_digit:
            continue

        # Filtro de tokens curtos (token.txt é o texto original do token, antes da lematização)
        if len(token.text) < 3:
            continue

        # Lematização
        lema = token.lemma_.lower()

        # Remoção de acentos do lema (para que o jaccard seja mais robusto a variações acentuadas)
        lema = _remove_accents(lema)

        # Limpeza final de pontuação residual no lema (caso a lematização introduza caracteres indesejados)
        lema = lema.strip(string.punctuation)

        # Validação final e adição ao conjunto
        if lema and len(lema) >= 3 and not lema.isdigit():
            # Adicionar ao set ignora automaticamente duplicatas (se o mesmo lema aparecer mais de uma vez no mesmo feedback, ele só contará como 1 para freq_global)
            conjunto_lemas.add(lema)

    return conjunto_lemas


def preprocess_feedbacks(
    feedbacks: list[str]
) -> tuple[list[set[str]], dict[str, int]]:
    # conjuntos_lemas[i] conterá o set de lemas do feedback i
    # A posição i espelha o ID do vértice no grafo — esta correspondência é a base do sistema inteiro
    conjuntos_lemas: list[set[str]] = []

    # freq_global acumula quantos feedbacks contêm cada lema
    freq_global: dict[str, int] = {}

    for i, feedback in enumerate(feedbacks):
        # Aplica o pipeline completo de PLN no feedback atual
        conjunto = _preprocess_single_feedback(feedback)

        # Armazena o conjunto na posição i, mantendo a correspondência com o id do vértice
        conjuntos_lemas.append(conjunto)

        # Atualiza freq_global com os lemas do feedback atual.
        # Para cada lema no conjunto (já sem duplicatas intra-feedback),
        # incrementamos o contador global de ocorrências.
        for lema in conjunto:
            freq_global = _increment_freq(freq_global, lema)

    return conjuntos_lemas, freq_global


# Bloco de execução direta (Este bloco só executa quando o arquivo é chamado diretamente com 'python src/preprocessing.py' (ignorado quando importado por main.py))
if __name__ == "__main__":

    CAMINHO_FEEDBACKS = "data/feedbacks.txt"

    print("=" * 60)
    print("  TESTE DO MÓDULO: preprocessing.py")
    print("  Issues #3, #4 e #5 — Integrante 1")
    print("=" * 60)

    # Leitura
    print(f"\n[ISSUE #3] Lendo feedbacks de '{CAMINHO_FEEDBACKS}'...")
    feedbacks_originais = read_feedbacks_txt(CAMINHO_FEEDBACKS)
    print(f"  → {len(feedbacks_originais)} feedbacks carregados.")
    print(f"  → Exemplo (vértice 0): \"{feedbacks_originais[0]}\"")

    # Pré-processamento
    print("\n[ISSUES #4 e #5] Pré-processando feedbacks com spaCy...")
    conjuntos_lemas, freq_global = preprocess_feedbacks(feedbacks_originais)

    print(f"\n  CONJUNTOS DE LEMAS (conjuntos_lemas):")
    for i, conjunto in enumerate(conjuntos_lemas):
        # Ordena o set para exibição determinística (sets não têm ordem)
        print(f"    Vértice {i:2d}: {sorted(conjunto)}")

    # Exibe os 10 lemas mais frequentes no corpus inteiro
    print(f"\n  FREQUÊNCIA GLOBAL (freq_global) — Top 10 lemas:")
    top_lemas = sorted(freq_global.items(), key=lambda x: x[1], reverse=True)
    for lema, freq in top_lemas[:10]:
        print(f"    '{lema}': {freq} feedback(s)")

    # Verifica se o contrato de tipos está correto
    print("\n  VERIFICAÇÃO DE TIPOS:")
    print(f"    type(conjuntos_lemas)    → {type(conjuntos_lemas)}")
    print(f"    type(conjuntos_lemas[0]) → {type(conjuntos_lemas[0])}")
    print(f"    type(freq_global)        → {type(freq_global)}")

    print("\n" + "=" * 60)
    print("  Módulo OK. Pronto para integração com similarity_graph.py")
    print("=" * 60)