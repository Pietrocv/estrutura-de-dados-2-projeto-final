# TopicGraph EJ

Detecção de tópicos em feedbacks de uma Empresa Júnior usando Processamento de Linguagem Natural, grafos e estruturas de dados implementadas manualmente.

O projeto transforma feedbacks textuais em um grafo de similaridade, identifica comunidades de documentos semelhantes, separa outliers e gera um relatório com métricas e visualizações.

## Participantes

| Participante | Nome |
|---|---|
| Participante 1 | Arthur Scartezini |
| Participante 2 | Pietro Calegari Visentin |
| Participante 3 | Pedro Ian |
| Participante 4 | Guilherme Negreiros |
| Participante 5 | Guilherme Mendes |

## Objetivo

O objetivo é identificar temas recorrentes em feedbacks escritos em linguagem natural. Cada feedback é tratado como um vértice de um grafo. A similaridade entre feedbacks define as arestas e seus pesos. Depois, o sistema usa algoritmos de grafos para encontrar comunidades, que representam possíveis tópicos.

Exemplos de tópicos detectáveis:

- comunicação e alinhamento;
- prazos, atrasos e cronograma;
- qualidade técnica;
- orçamento e escopo;
- suporte pós-entrega;
- apresentação, documentação e materiais.

## Visão Geral do Pipeline

```text
Arquivo .txt ou gerador automático
        |
        v
Pré-processamento com spaCy
        |
        v
Conjuntos de lemas por feedback
        |
        v
Similaridade de Jaccard
        |
        v
Matriz de adjacência ponderada
        |
        v
Grafo de similaridade filtrado
        |
        v
Prim Máximo
        |
        v
Corte de arestas fracas
        |
        v
Comunidades + outliers
        |
        v
Nomeação dos tópicos, métricas e visualizações
```

## Como o Sistema Modela o Problema

| Elemento | Representação no projeto |
|---|---|
| Feedback | Vértice do grafo |
| Similaridade entre dois feedbacks | Aresta ponderada |
| Peso da aresta | Índice de Jaccard entre os conjuntos de lemas |
| Grafo | Não direcionado e ponderado |
| Estrutura principal | Matriz de adjacência |
| Comunidade | Componente conexo após filtragem/corte |
| Outlier | Feedback isolado sem similaridade suficiente para anexação |

## Pré-processamento

O arquivo de entrada deve conter um feedback por linha. O sistema lê esses textos e aplica:

- conversão para minúsculas;
- remoção de pontuação;
- tokenização com `spaCy`;
- lematização com `pt_core_news_sm`;
- remoção de acentos após a lematização;
- remoção de stopwords gerais;
- remoção de `CUSTOM_STOPWORDS` do domínio.

As `CUSTOM_STOPWORDS` removem termos muito genéricos para o objetivo do projeto, como `empresa`, `equipe`, `projeto`, `bem`, `boa`, `durante` e `muito`. Isso evita conexões artificiais entre feedbacks que compartilham apenas palavras comuns, mas não necessariamente o mesmo assunto.

## Similaridade de Jaccard

Cada feedback vira um conjunto de lemas. A similaridade entre dois feedbacks é calculada manualmente pelo índice de Jaccard:

```text
J(A, B) = |A interseção B| / |A união B|
```

Exemplo:

```text
A = {comunicacao, cliente, reuniao}
B = {comunicacao, prazo, reuniao}

interseção = 2
união = 4
Jaccard = 0.50
```

O valor `0` indica nenhuma palavra relevante compartilhada. O valor `1` indica conjuntos iguais.

## Grafo e Métricas

Após o cálculo de Jaccard, o sistema monta uma matriz de adjacência `N x N`, onde `N` é a quantidade de feedbacks.

O limiar de relevância atual é:

```text
LIMIAR_RELEVANCIA = 0.20
```

Esse limiar define quais arestas são consideradas relevantes para métricas como:

- grau médio;
- densidade;
- triângulos/cliques K3.

Importante: os triângulos são contados antes da Árvore Geradora Máxima, no grafo de similaridade filtrado. Se a contagem fosse feita depois da árvore, a métrica perderia sentido, já que árvores praticamente eliminam ciclos.

## Prim Máximo

O projeto usa Prim Máximo, não Prim Mínimo.

Como pesos maiores significam maior similaridade, o Prim Máximo preserva as conexões semânticas mais fortes entre os feedbacks. O Prim Mínimo faria o contrário: priorizaria feedbacks pouco semelhantes.

Depois da AGM máxima, o sistema remove arestas fracas para separar os grupos.

```text
LIMIAR_CORTE = 0.20
```

## Comunidades e Outliers

Após o corte de arestas fracas, o sistema encontra componentes conexos com busca em profundidade iterativa.

Componentes com apenas um vértice são tratados como candidatos a outlier. Antes de classificá-los definitivamente, o sistema tenta anexá-los à comunidade mais semelhante.

```text
LIMIAR_ANEXACAO = 0.30
```

Se a maior similaridade encontrada for menor que `0.30`, o feedback permanece separado como outlier. Assim, comunidades e outliers não são misturados artificialmente.

## Nomeação dos Tópicos

As comunidades são detectadas antes de receber qualquer nome.

Depois da detecção, o sistema usa uma tabela hash manual para contar os termos das comunidades. Os termos mais representativos são escolhidos considerando frequência local e raridade global. A partir deles, o sistema gera nomes automáticos como:

```text
Alinhamento / Claro / Comunicacao
Atraso / Data / Planejamento
Codigo / Facil / Manter
```

## Algoritmos e Estruturas Implementados

| Componente | Arquivo | Descrição |
|---|---|---|
| Pré-processamento | `src/preprocessing.py` | Leitura, normalização, stopwords, lematização e geração dos conjuntos de lemas |
| Jaccard | `src/similarity_graph.py` | Similaridade manual entre conjuntos |
| Matriz de adjacência | `src/similarity_graph.py` | Grafo ponderado representado por lista de listas |
| Grau médio e densidade | `src/similarity_graph.py` | Métricas do grafo filtrado |
| Prim Máximo | `src/prim_max.py` | Árvore Geradora Máxima implementada manualmente |
| Comunidades | `src/communities.py` | Corte de arestas, DFS/BFS e tratamento de outliers |
| Triângulos K3 | `src/analysis.py` | Contagem de cliques de tamanho 3 no grafo filtrado |
| HashTable manual | `src/analysis.py` | Estrutura própria para contagem de termos |
| Análise e tópicos | `src/analysis.py` | Palavras-chave, nomes de tópicos e métricas finais |
| Pipeline do app | `src/app_pipeline.py` | Geração de feedbacks, relatório e SVGs para a API |

## Estrutura do Repositório

```text
estrutura-de-dados-2-projeto-final/
|
|-- api/
|   |-- app.py                    # API FastAPI
|
|-- data/
|   |-- feedbacks.txt             # Base principal
|   |-- feedbacks_133.txt         # Base pronta com 133 feedbacks
|   |-- feedbacks_200.txt         # Base pronta com 200 feedbacks
|   |-- feedbacks_250.txt         # Base pronta com 250 feedbacks
|
|-- docs/
|   |-- Documento_Tecnico_PLN.pdf # Documento técnico do projeto
|
|-- frontend/
|   |-- public/
|   |   |-- presentation.html     # Apresentação aberta pelo app
|   |-- src/
|   |   |-- App.jsx               # Interface React
|   |   |-- styles.css            # Estilos do app
|   |-- package.json
|
|-- output/
|   |-- vertices_iniciais_150.svg
|   |-- grafo_relevante_150.svg
|   |-- comunidades_detectadas_150.svg
|
|-- src/
|   |-- preprocessing.py
|   |-- similarity_graph.py
|   |-- prim_max.py
|   |-- communities.py
|   |-- analysis.py
|   |-- app_pipeline.py
|
|-- main.py                       # Execução via terminal
|-- presentation.html             # Cópia standalone da apresentação
|-- requirements.txt              # Dependências Python
|-- start-app.ps1                 # Inicialização rápida do app no Windows
|-- README.md
```

## Bases de Feedbacks

O diretório `data/` contém bases prontas para teste:

| Arquivo | Quantidade |
|---|---:|
| `data/feedbacks_133.txt` | 133 feedbacks |
| `data/feedbacks_200.txt` | 200 feedbacks |
| `data/feedbacks_250.txt` | 250 feedbacks |

O limite atual do app é de 250 feedbacks. Esse limite foi definido para manter os SVGs gerados leves, legíveis e adequados para demonstração.

## Aplicação Web

O projeto possui uma interface web para executar a análise visualmente.

Tecnologias:

- React;
- Vite;
- FastAPI;
- SVG inline gerado pelo backend.

Na interface é possível:

- enviar um arquivo `.txt`;
- gerar feedbacks automaticamente;
- ver o relatório textual de métricas;
- expandir a lista de feedbacks analisados;
- visualizar três etapas do grafo:
  - vértices iniciais;
  - grafo de similaridade filtrado;
  - comunidades detectadas;
- clicar nos SVGs para expandir a visualização;
- abrir a apresentação do projeto pelo botão `Apresentação`.

## Como Executar o Pipeline pelo Terminal

### 1. Instalar dependências

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m spacy download pt_core_news_sm
```

### 2. Executar

```powershell
python main.py
```

Por padrão, o pipeline usa `data/feedbacks.txt`.

## Como Executar o App

### Opção rápida no Windows

Na raiz do projeto:

```powershell
.\start-app.ps1
```

Depois acesse:

```text
http://localhost:5173
```

Se o PowerShell bloquear o script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start-app.ps1
```

### Opção manual

Terminal 1, backend:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.app:app --host 127.0.0.1 --port 8000
```

Terminal 2, frontend:

```powershell
cd frontend
npm install
npm run dev -- --host localhost --port 5173
```

Depois abra:

```text
http://localhost:5173
```

A apresentação fica disponível em:

```text
http://localhost:5173/presentation.html
```

## Resultado de Referência com 250 Feedbacks

Uma execução real com 250 feedbacks gerados pelo sistema apresentou:

| Métrica | Valor |
|---|---:|
| Feedbacks analisados | 250 |
| Lemas únicos | 171 |
| Matriz de adjacência | 250 x 250 |
| Grau médio inicial | 34.35 |
| Densidade inicial | 0.1380 |
| Arestas na AGM máxima | 232 |
| Comunidades detectadas | 6 |
| Outliers detectados | 20 |
| Triângulos K3 no grafo filtrado | 52.022 |

Tópicos detectados nessa execução:

| Tópico | Tamanho | Termos principais |
|---|---:|---|
| Tópico 1 | 39 | alinhamento, claro, comunicação |
| Tópico 2 | 39 | atraso, data, planejamento |
| Tópico 3 | 38 | código, fácil, manter |
| Tópico 4 | 38 | coerente, entregar, escopo |
| Tópico 5 | 38 | ajuste, correções, garantia |
| Tópico 6 | 38 | apresentação, gráfico, material |

Os 20 feedbacks restantes foram classificados como outliers.

## Dependências

### Python

As dependências Python estão em `requirements.txt`:

```text
spacy
click
fastapi
uvicorn[standard]
python-multipart
```

### Frontend

As dependências do frontend estão em `frontend/package.json`:

```text
react
react-dom
vite
@vitejs/plugin-react
lucide-react
```

## Restrições do Projeto

Os algoritmos centrais de grafos e estruturas de dados foram implementados manualmente.

O projeto não usa:

- `networkx`;
- `sklearn`;
- `scipy`;
- algoritmos prontos de comunidades;
- bibliotecas prontas para similaridade textual.

O `spaCy` é usado apenas para tarefas linguísticas de PLN, como tokenização, stopwords e lematização.

## Build do Frontend

Para validar o frontend:

```powershell
cd frontend
npm run build
```

## Materiais de Apoio

- `docs/Documento_Tecnico_PLN.pdf`: documento técnico do projeto.
- `presentation.html`: apresentação standalone.
- `frontend/public/presentation.html`: apresentação aberta pelo app.

## Situação Atual

O projeto atualmente possui:

- pipeline completo via terminal;
- API FastAPI;
- frontend React/Vite;
- geração automática de feedbacks;
- upload de arquivos `.txt`;
- relatório textual;
- visualizações SVG;
- apresentação integrada;
- bases prontas em `data/`.

Projeto desenvolvido para a disciplina de Estruturas de Dados 2.
