# Roteiro de apresentação — TopicGraph EJ

**Grupo:** 13  
**Duração planejada:** 22 a 24 minutos  
**Formato:** 24 slides, cinco blocos naturais de assunto  
**Navegação:** setas esquerda/direita; `F` ativa tela cheia

## Visão geral da divisão

| Pessoa | Slides | Tema | Tempo |
|---|---:|---|---:|
| Pessoa 1 | 1–7 | Problema, entrada e PLN com spaCy | 4min30s |
| Pessoa 2 | 8–11 | Jaccard, grafo, matriz e métricas | 4min |
| Pessoa 3 | 12–14 | Prim Máximo e redução de ruído | 4min |
| Pessoa 4 | 15–17 | Corte, comunidades e outliers | 4min |
| Pessoa 5 | 18–24 | HashTable, interpretação, resultados, app e conclusão | 6min |

> Os slides não exibem nomes ou números de integrantes. A troca de apresentador acontece pelas mudanças naturais de assunto.

---

## Pessoa 1 — Slides 1 a 7 — Dados e PLN com spaCy

**Tempo estimado:** 4min30s

### Slide 1 — Título

“Somos o Grupo 13 e nosso projeto se chama TopicGraph EJ. O objetivo é detectar tópicos recorrentes em feedbacks de uma Empresa Júnior combinando Processamento de Linguagem Natural e algoritmos de grafos. Em vez de ler cada comentário isoladamente, queremos transformar os textos em comunidades que representem assuntos como comunicação, prazo, qualidade, orçamento ou suporte.”

“Na demonstração, o próprio app gera 250 feedbacks e executa a análise na hora. Essa geração produz seis comunidades temáticas. Um ponto importante é que os algoritmos centrais de estruturas de dados foram implementados manualmente.”

### Slide 2 — Contexto

“Empresas Juniores recebem feedbacks de clientes, membros e projetos. Esses dados costumam estar em formulários, mensagens, relatórios ou conversas de encerramento. O problema é que texto livre não vem organizado em categorias.”

“Quando o volume cresce, a análise manual fica lenta e subjetiva. Também é fácil perceber um comentário muito negativo e não perceber um padrão moderado que aparece dezenas de vezes. Por isso, a relevância do projeto está em apoiar a priorização: descobrir quais temas são recorrentes e merecem ação.”

### Slide 3 — Objetivo

“A proposta tem três transformações. Primeiro, o texto vira uma representação comparável. Depois, a similaridade vira um grafo ponderado. Por fim, a estrutura do grafo é usada para separar comunidades, e cada comunidade é interpretada como um tópico.”

“A nomeação não interfere na formação dos grupos. Isso é importante porque reduz o risco de encaixar os dados à força em categorias escolhidas antes da análise.”

### Slide 4 — Pipeline

“Este é o pipeline completo. Lemos os feedbacks; aplicamos PLN; calculamos Jaccard para todos os pares; montamos a matriz do grafo; extraímos uma árvore geradora máxima com Prim; removemos conexões fracas; encontramos componentes conexos com DFS; e finalmente extraímos termos para nomear os tópicos.”

“Cada etapa responde a uma pergunta: o que há no texto, com quais documentos ele se parece e a qual grupo ele pertence.”

### Slide 5 — Entrada

“A entrada principal é um arquivo TXT com um feedback por linha. Linhas vazias são ignoradas e, se a primeira linha for a palavra ‘feedback’, ela é tratada como cabeçalho.”

“A posição do feedback na lista define o ID do vértice. Então `feedbacks[i]`, `conjuntos_lemas[i]` e o vértice `i` sempre representam o mesmo documento. Essa correspondência é a base de integração entre os módulos.”

“No aplicativo web, também é possível enviar o TXT ou gerar entre 10 e 250 feedbacks de teste. Na apresentação, vamos gerar 250 na hora.”

### Slide 6 — PLN aplicado

“O pré-processamento está em `src/preprocessing.py`. Primeiro o texto é convertido para minúsculas e a pontuação é removida. Em seguida, o modelo de português `pt_core_news_sm` do spaCy realiza tokenização e lematização.”

“Filtramos stopwords do spaCy, espaços, pontuação residual, dígitos e tokens com menos de três caracteres. O projeto também possui uma lista de stopwords do domínio, com termos muito genéricos como ‘empresa’, ‘equipe’ e ‘projeto’, que poderiam aproximar documentos sem representar um tópico específico.”

“Depois da lematização, removemos acentos para reduzir variações de escrita. O resultado de cada documento é um conjunto de lemas.”

### Slide 7 — Conjuntos de lemas

“Neste exemplo, o texto sobre demora nas mensagens e dificuldade de alinhamento vira um conjunto com termos como ‘mensagem’, ‘demorar’, ‘responder’ e ‘alinhamento’.”

“Usamos conjunto porque o Jaccard considera presença ou ausência. Se uma palavra aparecer várias vezes dentro do mesmo feedback, ela continua sendo um único elemento do conjunto. Isso reduz a influência de repetição artificial em um documento curto.”

### Transição para a Pessoa 2

“Com cada feedback representado por um conjunto de lemas, já podemos comparar os documentos. A próxima parte explica como essa comparação é feita manualmente e como ela se transforma no grafo.”

### Perguntas técnicas prováveis — Pessoa 1

**Por que remover acentos somente depois da lematização?**  
Porque o modelo linguístico recebe o texto preservando a grafia normal do português, o que favorece sua análise. A normalização de acentos é aplicada ao lema final para padronizar a comparação.

**Por que remover palavras como ‘projeto’ e ‘equipe’?**  
Porque aparecem em muitos feedbacks independentemente do assunto. Elas aumentariam a similaridade entre tópicos diferentes sem acrescentar poder discriminativo.

**Por que usar `set` e não uma lista com frequência?**  
Porque a medida escolhida é Jaccard, definida sobre conjuntos. A frequência é usada posteriormente, na interpretação das comunidades.

**spaCy faz o agrupamento?**  
Não. spaCy é usado apenas na etapa linguística: tokenização, stopwords e lematização. O agrupamento vem dos algoritmos implementados no projeto.

---

## Pessoa 2 — Slides 8 a 11 — Jaccard e grafo ponderado

**Tempo estimado:** 4 minutos

### Slide 8 — Jaccard

“O índice de Jaccard divide o tamanho da interseção pelo tamanho da união. Na implementação manual, percorremos um conjunto, contamos quantos elementos também estão no outro e calculamos a união por `|A| + |B| - |interseção|`.”

“No exemplo, dois dos quatro termos distintos são compartilhados, então a similaridade é 0,50. A medida é adequada porque nossa representação já é um conjunto de lemas, é simples de interpretar e não depende de uma biblioteca pronta de similaridade.”

“Se os dois conjuntos estiverem vazios, o código retorna zero, evitando divisão por zero e evitando considerar dois documentos sem termos válidos como semelhantes.”

### Slide 9 — Grafo ponderado

“Cada feedback é um vértice. A relação entre dois documentos é uma aresta, e o peso dessa aresta é o Jaccard. Como a similaridade de A com B é igual à de B com A, o grafo é não direcionado e a matriz é simétrica.”

“Conceitualmente comparamos todos os pares. Para métricas e visualização, uma aresta é considerada relevante quando o peso é maior ou igual a 0,20.”

### Slide 10 — Matriz de adjacência

“A representação escolhida é uma matriz N por N. O acesso ao peso entre dois vértices é direto, em O(1), e a construção é coerente com a comparação todos contra todos.”

“A matriz também combina com a implementação do Prim, que a cada iteração examina os possíveis vizinhos. A desvantagem é o custo O(V²) de memória, mas para os 250 documentos gerados pelo app isso é aceitável no escopo do trabalho.”

“A diagonal é zero porque não precisamos representar a similaridade de um documento consigo mesmo.”

### Slide 11 — Grau, grau médio, densidade e cliques

“Com limiar 0,20, a geração de 250 feedbacks encontrou 5.084 arestas relevantes. O grau de um vértice é a quantidade de vizinhos acima desse limiar. A média dos graus foi 40,67.”

“A densidade é a quantidade de arestas relevantes dividida pelo total possível. Para 250 vértices existem 31.125 pares possíveis; 5.084 divididos por 31.125 resultam em 0,1633.”

“Também contamos triângulos, ou cliques K3. Foram 67.240. Um triângulo representa três feedbacks mutuamente conectados acima do limiar, servindo como indício de coesão local. Esse número não significa 67.240 tópicos; é uma métrica estrutural.”

### Transição para a Pessoa 3

“O grafo ainda possui muitas conexões redundantes. Para obter uma estrutura mais simples, mas preservar as relações fortes, aplicamos uma árvore geradora máxima.”

### Perguntas técnicas prováveis — Pessoa 2

**Qual é a complexidade da construção da matriz?**  
São comparados todos os pares, portanto há O(V²) comparações. O custo de cada Jaccard depende do tamanho dos conjuntos de lemas; considerando tamanho médio `L`, pode ser descrito como O(V²·L).

**Por que não usar similaridade de cosseno ou embeddings?**  
Jaccard é coerente com a representação em conjuntos, interpretável e implementável manualmente dentro das restrições da disciplina. Cosseno exigiria vetores de frequência; embeddings adicionariam modelos e ocultariam parte relevante do processamento.

**O limiar 0,20 cria a matriz?**  
Não. A matriz armazena todos os pesos. O limiar define quais pesos contam como arestas relevantes nas métricas e visualizações.

**Por que existem tantos triângulos em um grafo com baixa densidade?**  
Porque as arestas se concentram dentro das comunidades. Um grafo globalmente esparso pode ter regiões locais bastante densas.

---

## Pessoa 3 — Slides 12 a 14 — Prim Máximo

**Tempo estimado:** 4 minutos

### Slide 12 — Árvore Geradora Máxima

“A função `prim_maximum_spanning_tree`, em `src/prim_max.py`, constrói uma árvore geradora máxima. Ela mantém três vetores: `in_mst`, indicando os vértices já escolhidos; `key`, com o melhor peso conhecido para conectar cada vértice; e `parent`, com o vértice que fornece essa conexão.”

“Começamos no vértice zero. Em cada rodada, escolhemos fora da árvore o vértice com maior chave. Depois examinamos sua linha na matriz e atualizamos os vizinhos quando encontramos um peso maior.”

“Com os 250 feedbacks gerados, a implementação retorna 247 arestas. Tecnicamente, o resultado é uma floresta geradora máxima: alguns blocos temáticos não possuem ligação positiva entre si, então o Prim não força arestas de peso zero.”

### Slide 13 — Por que Prim Máximo

“Em problemas clássicos de custo, usa-se Prim mínimo. Aqui, porém, o peso representa similaridade. Peso alto é uma relação desejável. Usar o mínimo priorizaria documentos pouco semelhantes.”

“Por isso invertemos o critério: selecionamos a maior chave e atualizamos quando encontramos peso maior. A implementação tem O(V²), pois para cada vértice percorremos os vetores e a linha correspondente da matriz.”

“O Prim combina bem com a matriz porque consultar qualquer peso é simples e direto. Não precisamos converter o grafo para outra estrutura antes do algoritmo.”

### Slide 14 — Redução de ruído

“A redução é grande: saímos de 5.084 arestas relevantes para 247 arestas na floresta. Ciclos e conexões redundantes são removidos, mantendo uma espinha dorsal com as melhores ligações necessárias em cada componente alcançável.”

“Entretanto, a árvore geradora tem como objetivo manter os vértices conectados. Isso significa que ela pode conservar uma aresta relativamente fraca apenas porque essa aresta é a melhor ponte disponível entre dois blocos. Essas pontes serão tratadas na próxima etapa.”

### Transição para a Pessoa 4

“A AGM simplifica o grafo, mas ainda não entrega as comunidades. Agora precisamos cortar as pontes fracas e percorrer a estrutura resultante.”

### Perguntas técnicas prováveis — Pessoa 3

**A AGM contém necessariamente as 149 maiores arestas do grafo?**  
Não. Ela contém a combinação de arestas de maior peso que conecta os vértices sem formar ciclos. Uma aresta muito alta pode ficar de fora se fechar um ciclo.

**O que acontece se o grafo tiver vértices sem nenhuma aresta positiva?**  
O `parent` permanece `-1`; o código não adiciona aresta para esse vértice e emite um aviso. Ele será tratado como possível isolado/outlier.

**Por que não ordenar todas as arestas e usar Kruskal?**  
Kruskal também seria possível, mas exigiria uma lista de arestas e uma estrutura de conjuntos disjuntos. Como o projeto já usa matriz, Prim O(V²) é uma escolha direta e didática.

**A AGM já remove ruído?**  
Ela remove redundância estrutural, mas não define sozinha o que é ruído semântico. O corte por limiar é que remove as pontes consideradas fracas.

---

## Pessoa 4 — Slides 15 a 17 — Corte, comunidades e outliers

**Tempo estimado:** 4 minutos

### Slide 15 — Corte de arestas

“As arestas da floresta máxima são ordenadas por peso. As que têm peso menor que 0,20 são removidas. Na geração de 250 feedbacks, três arestas são cortadas, separando as seis comunidades.”

“A interpretação é que essas arestas funcionavam como pontes fracas entre grupos que internamente possuem relações mais fortes. Ao removê-las, uma única árvore se divide em várias componentes.”

“O limiar é um parâmetro empírico. Se for muito baixo, tópicos diferentes permanecem unidos. Se for muito alto, um tópico pode se fragmentar e gerar isolados.”

### Slide 16 — Detecção de comunidades

“Depois do corte, construímos uma lista de adjacência apenas com as arestas mantidas. A função principal usa DFS iterativa: para cada vértice não visitado, abre uma pilha e visita todos os vizinhos alcançáveis.”

“Cada conjunto alcançável é um componente conexo e, no nosso modelo, uma comunidade de feedbacks semanticamente relacionados.”

“O arquivo também implementa BFS com fila. Ela é auxiliar e pode validar que o particionamento em componentes é o mesmo. A DFS é a usada no pipeline principal.”

### Slide 17 — Outliers

“Uma componente de tamanho um recebe tratamento especial. Para esse vértice, o algoritmo procura a maior similaridade com qualquer vértice das comunidades não unitárias.”

“Se o melhor peso for pelo menos 0,20, o isolado é anexado à comunidade do melhor vizinho e essa ligação é adicionada ao grafo final. Caso contrário, ele é removido da lista de comunidades e classificado como outlier.”

“Na geração de 250 feedbacks, não houve outliers. Isso significa que todos os documentos tiveram evidência suficiente para permanecer em algum grupo; não significa que o tratamento seja desnecessário em outras bases.”

### Transição para a Pessoa 5

“Neste ponto as comunidades já existem. Falta interpretar cada grupo, medir os resultados e mostrar como o aplicativo apresenta todo o processo.”

### Perguntas técnicas prováveis — Pessoa 4

**Por que componente conexo pode representar uma comunidade?**  
Porque, depois da AGM e do corte, os caminhos restantes são formados por relações consideradas fortes. Um componente é um conjunto que continua semanticamente conectado sem depender das pontes fracas removidas.

**DFS e BFS produzem a mesma comunidade?**  
Sim, para componentes conexos em um grafo não direcionado. Elas podem visitar em ordens diferentes, mas alcançam o mesmo conjunto de vértices.

**Anexar um singleton não desfaz o corte?**  
Não de forma arbitrária. A anexação usa a matriz original e exige o mesmo limiar de 0,20. É uma regra específica para evitar tratar como tópico separado um documento que ainda possui uma relação relevante com outro grupo.

**Por que não deixar todo singleton como comunidade?**  
Porque uma comunidade de um documento não demonstra recorrência. O sistema tenta distinguir um comentário relacionado, mas desconectado pelo corte, de um caso realmente atípico.

---

## Pessoa 5 — Slides 18 a 24 — Interpretação, resultados, app e conclusão

**Tempo estimado:** 6 minutos

### Slide 18 — Tabela Hash manual

“Para interpretar as comunidades, o projeto implementa uma tabela hash própria em `src/analysis.py`. A função hash soma os códigos dos caracteres da chave e aplica módulo 37.”

“Cada posição da tabela é um bucket com uma lista. Quando duas palavras chegam ao mesmo índice, usamos encadeamento separado. Ao incrementar uma palavra, procuramos no bucket; se ela existir, aumentamos o valor, e se não existir, inserimos um novo elemento com valor um.”

“Essa estrutura conta a frequência dos lemas dentro de cada comunidade sem usar uma implementação pronta de tabela de frequência.”

### Slide 19 — Nomeação

“A frequência sozinha pode destacar palavras genéricas. Por isso a pontuação combina duas ideias: proporção local e raridade entre comunidades.”

“A proporção local é a frequência do termo dividida pelo tamanho da comunidade. A raridade usa uma expressão logarítmica semelhante à ideia de IDF: termos que aparecem em poucas comunidades recebem mais peso.”

“Os três termos de maior pontuação formam o nome automático. Na execução, por exemplo, a segunda comunidade recebeu ‘Etapa / Atraso / Prazo’. Podemos interpretar isso de forma mais natural como ‘Atrasos e gestão de prazos’.”

“É essencial reforçar: a nomeação ocorre depois da detecção e não altera os grupos.”

### Slide 20 — Resultados

“Ao gerar 250 feedbacks no app, obtivemos 56 lemas únicos, uma matriz 250 por 250, 247 arestas na floresta máxima, seis comunidades e zero outliers.”

“As seis comunidades correspondem aos temas usados pelo gerador: comunicação, prazos, qualidade técnica, orçamento, suporte pós-entrega e documentação/apresentação.”

“A distribuição é quase uniforme: quatro comunidades têm 42 feedbacks e duas têm 41. Isso é esperado porque o gerador intercala seis modelos temáticos até completar 250 textos.”

### Slide 21 — Demonstração do app

“Na demonstração do aplicativo, mostrar nesta ordem:

1. A área de entrada e o upload de um TXT.
2. A alternativa ‘Gerar e analisar’.
3. Os seis cartões de métricas.
4. O relatório textual expansível.
5. O fluxo visual completo.
6. As três visualizações: vértices iniciais, grafo filtrado e comunidades nomeadas.
7. A expansão de uma visualização em modal.”

“A interface é React com Vite, e a API é FastAPI. O endpoint `/upload` recebe o arquivo, `/generate` cria dados de teste e `/analyze` aceita uma lista de textos.”

### Slide 22 — Uso de LLM

“Se perguntarem sobre LLM, a resposta deve ser precisa: ela pode ter sido usada como apoio para dados fictícios, revisão de documentação ou organização da apresentação. O pipeline executado não chama uma LLM. Os algoritmos centrais estão implementados no repositório e geram os resultados localmente.”

### Slide 23 — Limitações

“O método tem vantagens de transparência e interpretabilidade, mas também limitações. Jaccard mede compartilhamento de lemas e não compreende sozinho sinônimos ou contexto profundo. Os limiares são empíricos. A matriz usa memória quadrática. Além disso, os textos gerados são controlados e contêm vocabulário recorrente; uma validação futura deveria usar feedbacks reais e mais ruidosos.”

### Slide 24 — Conclusão

“Como conclusão, o sistema transforma feedbacks dispersos em uma estrutura analisável. O PLN padroniza o texto; Jaccard mede a proximidade; o grafo representa as relações; Prim Máximo reduz a estrutura; o corte e a DFS revelam comunidades; e a HashTable ajuda a interpretar os temas. Assim, uma Empresa Júnior pode passar de comentários soltos para informação útil na tomada de decisão.”

“Obrigado. Estamos disponíveis para perguntas.”

### Perguntas técnicas prováveis — Pessoa 5

**A HashTable é usada para formar as comunidades?**  
Não. Ela é usada depois, para frequência e interpretação dos termos. As comunidades são formadas pelo grafo.

**A nomeação automática é uma LLM?**  
Não. É uma regra determinística baseada em frequência local e raridade do termo nas demais comunidades.

**Por que os nomes automáticos às vezes parecem pouco naturais?**  
Porque são compostos diretamente pelos três lemas mais pontuados. Um nome editorial mais fluido exige interpretação humana ou uma etapa adicional de geração textual.

**O que significam os 67.240 cliques?**  
O código detecta cliques de tamanho 3, isto é, triângulos no grafo filtrado. Eles medem coesão local e não equivalem ao número de comunidades.

**Qual foi o papel real do app?**  
Demonstrar o pipeline sem depender do terminal: receber dados, executar os mesmos módulos Python e apresentar métricas e SVGs da evolução do grafo.

**Como melhorar o projeto no futuro?**

- Avaliar dados reais rotulados ou revisados por especialistas.
- Comparar diferentes limiares de relevância, corte e anexação.
- Testar representações que considerem frequência ou semântica, mantendo uma linha de base interpretável.
- Substituir a matriz por uma representação esparsa quando a escala crescer muito.
- Avaliar estabilidade dos tópicos e qualidade da nomeação.

---

## Dados de referência para respostas rápidas

| Item | Valor/implementação |
|---|---|
| Demonstração no app | 250 feedbacks gerados na hora |
| Base adicional | 300 feedbacks |
| Lemas únicos na geração | 56 |
| Matriz | 250 × 250 |
| Limiar de relevância | 0,20 |
| Arestas relevantes | 5.084 |
| Grau médio | 40,67 |
| Densidade | 0,1633 |
| Arestas da floresta máxima | 247 |
| Comunidades | 6 |
| Outliers | 0 |
| Triângulos/cliques K3 | 67.240 |
| Limiar de corte | 0,20 |
| Limiar de anexação | 0,20 |
| HashTable | 37 buckets, soma de códigos dos caracteres, encadeamento separado |
| Prim Máximo | O(V²) na implementação com matriz |
| DFS | Iterativa, com pilha explícita |
| BFS | Auxiliar, com `deque` |

## Observação sobre dependências

Os algoritmos centrais não usam bibliotecas prontas de grafos ou similaridade. O spaCy é a dependência linguística. O aplicativo adicional usa FastAPI, Uvicorn, Python Multipart, React, Vite e Lucide React. Portanto, ao responder, diferencie “dependências do algoritmo central” de “dependências da interface web”.
