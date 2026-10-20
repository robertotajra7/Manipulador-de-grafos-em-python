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

## Estatísticas do grafo

A classe calcula o grau de cada vértice e as estatísticas solicitadas no trabalho.
Os atributos `numero_arestas`, `grau_minimo`, `grau_maximo` e `grau_medio`
retornam os valores correspondentes; o método `graus()` retorna o grau de cada
vértice e `estatisticas()` reúne todos os valores em um dicionário.

```python
from grafo import Grafo

grafo = Grafo(5, representacao="lista")
for u, v in [(1, 2), (2, 5), (5, 3), (4, 5), (1, 5)]:
    grafo.adicionar_aresta(u, v)

print(grafo.estatisticas())
```

Para o grafo de exemplo, as estatísticas esperadas são: 5 vértices, 5 arestas,
grau mínimo 1, grau máximo 4 e grau médio 2,0.

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


## Busca em largura (BFS)

O método `busca_em_largura(origem)` percorre o grafo a partir do vértice
inicial, usando uma fila FIFO. Ele retorna um dicionário indexado pelos
vértices; cada valor contém `pai` e `nivel`. A origem tem nível zero e pai
`None`. Vértices que não podem ser alcançados a partir da origem também são
listados, com pai e nível `None`.

Exemplo:

```python
from grafo import Grafo

grafo = Grafo(5, representacao="lista")
for u, v in [(1, 2), (2, 5), (5, 3), (4, 5), (1, 5)]:
    grafo.adicionar_aresta(u, v)

resultado = grafo.busca_em_largura(1)
for vertice, dados in resultado.items():
    print(vertice, dados["pai"], dados["nivel"])
```

A ordem de visita é determinística porque os vizinhos são consultados em ordem
crescente. O algoritmo usa `collections.deque` como fila, para remover o
próximo vértice em tempo eficiente. A gravação da árvore em arquivo será
implementada numa etapa posterior, junto com as operações de entrada e saída.
