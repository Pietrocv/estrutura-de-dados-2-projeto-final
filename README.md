# TopicGraph EJ - Detecção de Tópicos em Feedbacks de uma Empresa Júnior usando PLN e Grafos

> Projeto da disciplina de Estruturas de Dados 2 — Implementação manual de grafos, algoritmos e estruturas de dados aplicados à análise de texto com PLN.

---

## Sumário

- [Objetivo](#objetivo)
- [Como o Sistema Funciona](#como-o-sistema-funciona)
- [Modelagem do Grafo](#modelagem-do-grafo)
- [Algoritmos e Estruturas Implementados](#algoritmos-e-estruturas-implementados)
- [Restrições Técnicas](#restrições-técnicas)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Divisão de Responsabilidades](#divisão-de-responsabilidades)
- [Parâmetros Configuráveis](#parâmetros-configuráveis)
- [Dependências](#dependências)
- [Como Executar](#como-executar)
- [Exemplo de Entrada e Saída](#exemplo-de-entrada-e-saída)
- [Resultados Reais e Interpretação](#resultados-reais-e-interpretação)
- [Checklist de Entrega](#checklist-de-entrega)

---

## Objetivo

O sistema detecta **tópicos recorrentes** em feedbacks textuais de uma Empresa Júnior. Cada feedback é tratado como um documento. O sistema mede a similaridade entre os documentos, constrói um grafo ponderado com essas relações e identifica comunidades de feedbacks que falam sobre o mesmo assunto. Cada comunidade é então interpretada como um tópico — por exemplo: *atrasos e prazos*, *qualidade técnica*, *comunicação com o cliente*, *preço* ou *suporte pós-entrega*.

---

## Como o Sistema Funciona

O pipeline segue seis etapas em sequência:

```
feedbacks.txt
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  1. PRÉ-PROCESSAMENTO (PLN com spaCy)               │
│     lowercase → remoção de pontuação/acentos →      │
│     tokenização → remoção de stopwords →            │
│     lematização → conjuntos de lemas                │
└───────────────────────┬─────────────────────────────┘
                        │  list[set[str]]
                        ▼
┌─────────────────────────────────────────────────────┐
│  2. SIMILARIDADE                                    │
│     Cálculo manual do Índice de Jaccard entre       │
│     todos os pares de feedbacks                     │
└───────────────────────┬─────────────────────────────┘
                        │  matriz N×N de pesos
                        ▼
┌─────────────────────────────────────────────────────┐
│  3. MODELAGEM DO GRAFO                              │
│     Matriz de adjacência ponderada e não            │
│     direcionada; cálculo de grau médio e densidade  │
└───────────────────────┬─────────────────────────────┘
                        │  matriz_pesos
                        ▼
┌─────────────────────────────────────────────────────┐
│  4. ÁRVORE GERADORA MÁXIMA                          │
│     Algoritmo de Prim Máximo — preserva as          │
│     conexões semânticas mais fortes                 │
└───────────────────────┬─────────────────────────────┘
                        │  mst_edges
                        ▼
┌─────────────────────────────────────────────────────┐
│  5. DETECÇÃO DE COMUNIDADES                         │
│     Remoção de arestas fracas + DFS iterativa       │
│     para encontrar componentes conexos              │
│     Outliers: vértices sem comunidade adequada      │
└───────────────────────┬─────────────────────────────┘
                        │  comunidades, outliers
                        ▼
┌─────────────────────────────────────────────────────┐
│  6. ANÁLISE E EXTRAÇÃO                              │
│     HashTable manual para contagem de lemas;        │
│     extração de palavras-chave; nomeação de         │
│     tópicos; métricas finais e detecção de cliques  │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
                  relatório_resultados
```

---

## Modelagem do Grafo

| Elemento | Definição no projeto |
|---|---|
| **Vértice** | Um feedback textual da Empresa Júnior |
| **Aresta** | Relação de similaridade entre dois feedbacks |
| **Peso da aresta** | Índice de Jaccard entre os conjuntos de lemas dos dois feedbacks |
| **Tipo de grafo** | Não direcionado e ponderado |
| **Representação** | Matriz de adjacência N×N |

**Por que feedback como vértice?** Porque o objetivo é agrupar *documentos* semanticamente semelhantes. Cada comunidade resultante representa um tópico.

**Por que Jaccard?** Os feedbacks são representados como conjuntos de lemas. Jaccard mede a proporção de termos compartilhados entre dois conjuntos — é simples, interpretável e implementável manualmente sem bibliotecas externas.

```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|

Exemplo:
  A = {comunicacao, cliente, reuniao}
  B = {comunicacao, prazo, reuniao}
  Jaccard = 2 / 4 = 0.50
```

**Por que Prim Máximo e não mínimo?** Pesos maiores significam maior similaridade. O Prim Mínimo priorizaria relações fracas — o oposto do que o problema exige. O Prim Máximo preserva as conexões mais fortes, formando uma árvore que reflete os agrupamentos semânticos reais.

**Por que cortar arestas da árvore?** A árvore geradora mantém todos os vértices conectados, mas algumas arestas são "pontes fracas" entre tópicos distintos. Ao removê-las, os grupos naturais se separam em componentes conexos — que são as comunidades/tópicos.

---

## Algoritmos e Estruturas Implementados

Todos os algoritmos e estruturas centrais foram implementados **manualmente**, sem uso de bibliotecas prontas:

| Componente | Descrição | Arquivo |
|---|---|---|
| Índice de Jaccard | Cálculo manual via interseção e união de sets | `similarity_graph.py` |
| Matriz de Adjacência | Lista de listas N×N com pesos de similaridade | `similarity_graph.py` |
| Grau médio e Densidade | Métricas calculadas sobre arestas com peso ≥ limiar | `similarity_graph.py` |
| Prim Máximo | Árvore Geradora Máxima — complexidade O(V²) | `prim_max.py` |
| DFS Iterativa | Detecção de componentes conexos com pilha explícita | `communities.py` |
| BFS (auxiliar) | Validação dos componentes conexos com fila | `communities.py` |
| Detecção de Outliers | Anexação ou classificação de vértices isolados | `communities.py` |
| Detecção de Triângulos | Busca de cliques de tamanho 3 no grafo filtrado | `analysis.py` |
| Tabela Hash manual | Classe própria com função hash, buckets e encadeamento separado | `analysis.py` |
| Nomeação automática | Termos frequentes na comunidade ponderados pela raridade nos demais grupos | `analysis.py` |

---

## Restrições Técnicas

| Status | Biblioteca / Recurso |
|---|---|
| ✅ Permitido | `spaCy` — exclusivamente para tokenização, stopwords e lematização |
| ✅ Permitido | `unicodedata` — remoção de acentos (biblioteca padrão do Python) |
| ✅ Permitido | `string` — constantes de pontuação (biblioteca padrão do Python) |
| ❌ Proibido | `networkx` — grafos prontos |
| ❌ Proibido | `sklearn` — similaridade textual pronta |
| ❌ Proibido | `scipy` — cálculos matemáticos de similaridade |
| ❌ Proibido | `unidecode` — biblioteca externa para acentos |

> **Como verificar:** o arquivo `requirements.txt` lista exclusivamente `spacy`. Qualquer outra biblioteca externa presente no ambiente que não seja da stdlib do Python viola as restrições do enunciado.

---

## Estrutura do Repositório

```
projeto-pln-grafos/
│
├── data/
│   └── feedbacks.txt          # Base de dados de entrada (um feedback por linha)
│
├── src/
│   ├── preprocessing.py       # Integrante 1 — Leitura e pipeline de PLN
│   ├── similarity_graph.py    # Integrante 2 — Jaccard e matriz de adjacência
│   ├── prim_max.py            # Integrante 3 — Algoritmo de Prim Máximo
│   ├── communities.py         # Integrante 4 — Corte de arestas, DFS e outliers
│   └── analysis.py            # Integrante 5 — HashTable, palavras-chave e métricas
│
├── main.py                    # Integração do pipeline e execução principal
├── requirements.txt           # Dependências do projeto
└── README.md
```

---

## Divisão de Responsabilidades

| Integrante | Módulo | Responsabilidade principal |
|---|---|---|
| **Integrante 1** | `preprocessing.py` | Leitura do arquivo, normalização, tokenização, remoção de stopwords, lematização e geração dos conjuntos de lemas |
| **Integrante 2** | `similarity_graph.py` | Implementação manual do Jaccard, construção da matriz de adjacência, grau médio e densidade |
| **Integrante 3** | `prim_max.py` | Implementação manual da Árvore Geradora Máxima via Prim Máximo |
| **Integrante 4** | `communities.py` | Remoção de arestas fracas, DFS iterativa para componentes conexos e tratamento de outliers |
| **Integrante 5** | `analysis.py` | HashTable manual, extração de palavras-chave por comunidade, nomeação de tópicos e métricas finais |

---

## Parâmetros Configuráveis

Os parâmetros abaixo podem ser ajustados em `main.py` para calibrar os resultados conforme a base de dados utilizada:

| Parâmetro | Valor inicial sugerido | Efeito |
|---|---|---|
| `LIMIAR_RELEVANCIA` | `0.10` – `0.15` | Define o peso mínimo para uma aresta ser contada no cálculo de grau médio, densidade e cliques |
| `LIMIAR_CORTE` | `0.15` – `0.20` | Define o peso abaixo do qual uma aresta da árvore é removida para separar comunidades |
| `LIMIAR_ANEXACAO` | `0.20` | Define a similaridade mínima para anexar um vértice isolado a uma comunidade existente |
| `MIN_TAMANHO_COMUNIDADE` | `2` | Comunidades com apenas 1 vértice são tratadas como possíveis outliers |
| `TOP_K_TERMOS` | `5` | Quantidade de palavras-chave extraídas por comunidade para nomeação do tópico |

> **Dica de calibração:** se o sistema gerar muitos outliers, reduza `LIMIAR_CORTE`. Se gerar uma única comunidade grande, aumente-o. Execute com dois ou três valores e compare o número de comunidades resultantes.

---

## Dependências

O projeto utiliza apenas a biblioteca `spaCy` como dependência externa. Todo o restante usa a stdlib do Python.

**`requirements.txt`:**
```
spacy>=3.0.0
```

---

## Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/<seu-usuario>/estrutura-de-dados-2-projeto-final.git
```

### 2. Crie e ative um ambiente virtual

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar no Linux/macOS
source venv/bin/activate

# Ativar no Windows
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Baixe o modelo de português do spaCy

```bash
python -m spacy download pt_core_news_sm
```

> **Atenção:** este passo é obrigatório. Sem o modelo de língua portuguesa, o módulo `preprocessing.py` lançará um erro na inicialização.

### 5. Adicione os feedbacks de entrada

Certifique-se de que o arquivo `data/feedbacks.txt` existe e contém os feedbacks, **um por linha**:

```
A comunicação com o cliente foi excelente durante todo o projeto.
O projeto atrasou e a entrega final passou do prazo.
Gostei da qualidade técnica do sistema entregue.
As reuniões de alinhamento foram confusas no começo.
O suporte pós-entrega foi rápido e atencioso.
```

> Linhas em branco são ignoradas automaticamente. A ordem das linhas define o ID de cada vértice no grafo (linha 0 = vértice 0, linha 1 = vértice 1, etc.).

O repositório também contém `data/feedbacks_300.txt`, uma base adicional com 300 feedbacks distintos para testes de maior escala. Para utilizá-la sem alterar o código, substitua temporariamente o conteúdo de `data/feedbacks.txt` pelo conteúdo dessa base ou passe seu caminho para `executar_pipeline`.

### 6. Execute o pipeline completo

```bash
python main.py
```

### 7. Verifique a saída

O sistema imprime no terminal as comunidades detectadas, os tópicos nomeados, as palavras-chave de cada grupo, os outliers e as métricas finais. As visualizações da execução usada na análise estão no diretório `output/`.

---

## Exemplo de Entrada e Saída

### Entrada (`data/feedbacks.txt`)

```
A comunicação com o cliente foi clara e constante.
Gostei das reuniões e do alinhamento com a equipe.
A entrega atrasou e o cronograma não foi cumprido.
O projeto teve atraso na entrega final.
O sistema ficou funcional e com boa qualidade técnica.
A solução entregue atendeu bem às necessidades.
```

### Saída esperada (terminal e relatório)

```
============================================================
  RELATÓRIO FINAL DE RESULTADOS
============================================================

Comunidades detectadas: 3
Outliers detectados:    0
Densidade do grafo:     0.47
Grau médio:             2.33
Triângulos encontrados: 1

------------------------------------------------------------
  COMUNIDADE 1 — Comunicação e Alinhamento
------------------------------------------------------------
  Feedbacks: [0, 1]
  Tamanho:   2
  Palavras-chave: comunicacao (2), cliente (2), reuniao (1), alinhamento (1), equipe (1)

  F0: "A comunicação com o cliente foi clara e constante."
  F1: "Gostei das reuniões e do alinhamento com a equipe."

------------------------------------------------------------
  COMUNIDADE 2 — Atrasos e Gestão de Prazos
------------------------------------------------------------
  Feedbacks: [2, 3]
  Tamanho:   2
  Palavras-chave: atrasar (2), entrega (2), cronograma (1), projeto (1), cumprir (1)

  F2: "A entrega atrasou e o cronograma não foi cumprido."
  F3: "O projeto teve atraso na entrega final."

------------------------------------------------------------
  COMUNIDADE 3 — Qualidade Técnica da Solução
------------------------------------------------------------
  Feedbacks: [4, 5]
  Tamanho:   2
  Palavras-chave: entregar (2), sistema (1), funcional (1), qualidade (1), solucao (1)

  F4: "O sistema ficou funcional e com boa qualidade técnica."
  F5: "A solução entregue atendeu bem às necessidades."

============================================================
  Fim do relatório
============================================================
```

---

## Resultados Reais e Interpretação

Os resultados abaixo correspondem à execução registrada nos arquivos SVG do diretório `output/`, usando os 150 feedbacks de `data/feedbacks.txt` e limiar de relevância igual a `0.20`.

### Resumo quantitativo

| Métrica | Resultado observado |
|---|---:|
| Feedbacks processados / vértices | 150 |
| Arestas com similaridade relevante | 577 |
| Limiar de similaridade de Jaccard | 0.20 |
| Comunidades detectadas | 11 |
| Outliers | 0 |
| Densidade do grafo filtrado | 0.0516 |
| Grau médio do grafo filtrado | 7.69 |

A densidade foi calculada por `577 / (150 × 149 / 2)`. O grau médio foi calculado por `2 × 577 / 150`.

O grafo é esparso: apenas aproximadamente 5,16% das arestas possíveis permaneceram após a filtragem. Mesmo assim, cada vértice possui em média 7,69 relações relevantes. Isso indica que o limiar removeu a maior parte das comparações fracas sem eliminar as conexões internas necessárias para formar os tópicos.

### Comunidades encontradas

| Comunidade | Quantidade | IDs dos feedbacks | Interpretação do tópico |
|---|---:|---|---|
| 1 | 16 | 0–15 | Comunicação, mensagens, reuniões e alinhamento |
| 2 | 16 | 16–31 | Prazos, cronograma, etapas e atrasos |
| 3 | 16 | 32–47 | Qualidade técnica, código, testes e validação |
| 4 | 14 | 48–61 | Preço, orçamento, custo-benefício e negociação |
| 5 | 14 | 62–75 | Suporte pós-entrega, treinamento, correções e garantia |
| 6 | 14 | 76–89 | Levantamento de requisitos, diagnóstico e definição de escopo |
| 7 | 7 | 90, 92, 94, 96, 98, 100 e 102 | Documentação, relatório, arquivos e limitações |
| 8 | 7 | 91, 93, 95, 97, 99, 101 e 103 | Apresentação, slides, recursos visuais e resumo |
| 9 | 14 | 104–117 | Atendimento, confiança, postura e relacionamento com o cliente |
| 10 | 13 | 118–130 | Infraestrutura e experiência de uso: sala, internet, estacionamento e formulário |
| 11 | 19 | 131–149 | Resultados, indicadores, evidências, impacto e tomada de decisão |

As comunidades 7 e 8 são um resultado especialmente relevante. Esses feedbacks estavam próximos na base por tratarem da comunicação dos resultados, mas o algoritmo separou corretamente dois subtemas: documentação escrita e apresentação visual. Isso mostra que o método não se limitou a separar os blocos maiores da base.

A comunidade 11 foi a maior, com 19 feedbacks, representando aproximadamente 12,67% da coleção. As comunidades 7 e 8 foram as menores, com 7 feedbacks cada, ou aproximadamente 4,67% da coleção por comunidade. Não houve outliers, portanto todos os documentos apresentaram similaridade suficiente para pertencer a algum grupo.

### Interpretação e limitações

Os agrupamentos são semanticamente coerentes com os assuntos presentes nos textos. Termos como `prazo`, `cronograma` e `atraso` aproximaram os feedbacks de planejamento, enquanto `codigo`, `teste` e `validacao` aproximaram os feedbacks de qualidade técnica. O mesmo comportamento ocorreu nos demais tópicos.

O resultado também deve ser interpretado considerando as seguintes limitações:

- O índice de Jaccard mede compartilhamento de lemas, mas não compreende sozinho sinônimos ou contexto profundo. Dois textos semanticamente semelhantes podem não se conectar se utilizarem vocabulários muito diferentes.
- Os dados são controlados e possuem vocabulário recorrente em cada temática. Isso facilita a formação de comunidades mais bem separadas do que seria esperado em uma base real e ruidosa.
- O valor `0.20` é um parâmetro empírico. Valores menores tendem a unir tópicos diferentes; valores maiores podem fragmentar um tópico e aumentar o número de outliers.
- A árvore geradora máxima preserva as relações mais fortes necessárias para conectar os vértices, mas descarta relações redundantes que ainda poderiam ser úteis em outras técnicas de detecção de comunidades.
- Os nomes apresentados na tabela são interpretações humanas dos termos e feedbacks de cada comunidade. O código produz palavras-chave automaticamente, mas a atribuição de um nome semântico final exige interpretação.

Assim, a execução demonstra que a combinação de pré-processamento linguístico, similaridade de Jaccard, filtragem, Prim Máximo e componentes conexos conseguiu recuperar os principais assuntos planejados para a coleção. O resultado é adequado como prova de funcionamento do método, mas uma avaliação futura com feedbacks reais e menos controlados seria necessária para medir sua capacidade de generalização.

### Nomeação automática posterior

As comunidades são detectadas antes de receber qualquer nome. A nomeação não
escolhe, cria ou altera os grupos encontrados pelo algoritmo de grafos.

Depois da detecção, o sistema conta os lemas de cada comunidade com a tabela
hash manual. Cada lema recebe uma pontuação que combina sua frequência dentro
da comunidade com sua raridade nas outras comunidades. Os três termos de maior
pontuação formam um rótulo automático, sem uma lista prévia de assuntos.

Exemplo:

```text
Comunidade detectada: [16, 17, 18, 19, ...]
Termos representativos: prazo, cronograma, atraso
Nome automático: Prazo / Cronograma / Atraso
```

O fluxo completo permanece:

```text
Textos -> grafo -> Prim Máximo -> corte de arestas -> comunidades
       -> termos representativos -> nome automático
```

Essa abordagem permite que um assunto inesperado receba um nome baseado nos
próprios dados, sem limitar a detecção a categorias definidas pelo grupo.

### Visualizações da execução

- `output/vertices_iniciais_150.svg`: os 150 documentos antes da criação das arestas;
- `output/grafo_relevante_150.svg`: o grafo filtrado, com 577 arestas e 11 componentes visuais;
- `output/comunidades_detectadas_150.svg`: as 11 comunidades finais e seus respectivos tamanhos.

---

*Projeto desenvolvido para a disciplina de Estruturas de Dados 2.*
