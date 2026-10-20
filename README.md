# Estruturas de Dados II — Avaliação I

Projeto acadêmico para implementar uma biblioteca de grafos não direcionados em Python.

## Formato do arquivo de entrada

O arquivo de entrada é um arquivo de texto com este formato:

1. A primeira linha contém o número de vértices `n`.
2. Cada linha seguinte contém uma aresta, representada por dois números inteiros `u v`.
3. Os vértices são identificados pelos números de `1` até `n`.
4. Como o grafo é não direcionado, uma aresta `u v` conecta os dois vértices nos dois sentidos. Não é necessário escrever a mesma aresta duas vezes.

O arquivo `grafos/exemplo.txt` representa um grafo pequeno usado para validar o programa durante o desenvolvimento.

## Plano de implementação

O trabalho será desenvolvido incrementalmente, com commits separados para as principais funcionalidades:

- representação por lista de adjacência;
- representação por matriz de adjacência;
- estatísticas do grafo;
- busca em largura (BFS);
- leitura e gravação de arquivos;
- experimentos de memória e tempo de execução.

As funcionalidades serão documentadas e testadas conforme forem implementadas.
