# Estruturas de Dados II — Avaliação I

Projeto acadêmico para implementar uma biblioteca de grafos não direcionados em Python.

## Formato do arquivo de entrada

1. A primeira linha contém o número de vértices `n`.
2. Cada linha seguinte contém uma aresta, representada por dois números inteiros `u v`.
3. Os vértices são identificados pelos números de `1` até `n`.
4. Como o grafo é não direcionado, uma aresta `u v` conecta os dois vértices nos dois sentidos. Não é necessário escrever a mesma aresta duas vezes.

O arquivo `grafos/exemplo.txt` representa um grafo pequeno usado para validar a biblioteca durante o desenvolvimento.

## Biblioteca atual

O módulo `grafo.py` contém a classe `Grafo`. Para selecionar uma representação, informe o parâmetro `representacao`:

```python
from grafo import Grafo

grafo_lista = Grafo(5, representacao="lista")
grafo_matriz = Grafo(5, representacao="matriz")
```

As duas representações oferecem os métodos `adicionar_aresta(u, v)` e `vizinhos(vertice)`. Apenas a estrutura escolhida é alocada em cada objeto.

## Executar os testes

```bash
python -m unittest -v
```

## Plano de implementação

O trabalho será desenvolvido incrementalmente, com commits separados para as principais funcionalidades:

- representação por lista de adjacência;
- representação por matriz de adjacência;
- estatísticas do grafo;
- busca em largura (BFS);
- leitura e gravação de arquivos;
- experimentos de memória e tempo de execução.

As funcionalidades serão documentadas e testadas conforme forem implementadas.
