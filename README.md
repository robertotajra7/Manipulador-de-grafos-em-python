# Estruturas de Dados II — Avaliação I

Projeto acadêmico para implementar uma biblioteca de grafos não direcionados em Python.

## Formato do arquivo de entrada

1. A primeira linha útil contém o número de vértices `n`.
2. Cada linha seguinte contém uma aresta, representada por dois números inteiros `u v`.
3. Os vértices são identificados pelos números de `1` até `n`.
4. Como o grafo é não direcionado, uma aresta `u v` conecta os dois vértices nos dois sentidos. Não é necessário escrever a mesma aresta duas vezes.
5. Linhas vazias e linhas iniciadas com `#` são ignoradas.

O arquivo `grafos/exemplo.txt` representa o grafo pequeno usado para validar a biblioteca.

## Biblioteca `grafo.py`

A classe `Grafo` permite escolher entre lista e matriz de adjacência:

```python
from grafo import Grafo

grafo_lista = Grafo(5, representacao="lista")
grafo_matriz = Grafo(5, representacao="matriz")
```

Também é possível carregar o grafo diretamente de um arquivo:

```python
grafo = Grafo.de_arquivo("grafos/exemplo.txt", representacao="lista")
print(grafo.estatisticas())
print(grafo.busca_em_largura(1))
```

A classe oferece operações para adicionar arestas, consultar vizinhos, obter o grau dos vértices, calcular as estatísticas pedidas no trabalho e executar a busca em largura (BFS). A BFS retorna o pai e o nível de cada vértice; vértices inalcançáveis têm pai e nível `None`.

Para o arquivo de exemplo, as estatísticas esperadas são 5 vértices, 5 arestas, grau mínimo 1, grau máximo 4 e grau médio 2,0.

## Executar o programa principal

Com a pasta principal do projeto aberta no terminal, execute:

```bash
python main.py grafos/exemplo.txt --representacao lista --origem 1
```

O argumento `--representacao` aceita `lista` ou `matriz`, e `--origem` define o vértice inicial da BFS. Os valores padrão são `lista` e `1`.

A execução cria dois arquivos na pasta `resultados/`:

- `estatisticas.txt`: número de vértices, número de arestas, grau mínimo, grau máximo e grau médio.
- `bfs_origem_1.txt`: pai e nível de cada vértice para a busca iniciada em 1.

Para alterar os caminhos dos arquivos, use `--saida-estatisticas` e `--saida-bfs`. Exemplo:

```bash
python main.py grafos/exemplo.txt \
  --representacao matriz \
  --origem 3 \
  --saida-estatisticas resultados/estatisticas_matriz.txt \
  --saida-bfs resultados/bfs_matriz_origem_3.txt
```

## Executar os testes

```bash
python -m unittest -v
```

Os testes verificam as duas representações, estatísticas, BFS, leitura de arquivos de entrada válidos e inválidos e geração dos arquivos de saída.

## Próximas funcionalidades

O projeto será desenvolvido incrementalmente com commits separados. A próxima etapa após entrada e saída será implementar e validar os experimentos de uso de memória e tempo de execução nos grafos disponibilizados para os estudos de caso.

## Experimentos de memória e tempo

O arquivo `experimentos.py` compara a lista e a matriz de adjacência usando a
mesma entrada. Por padrão, realiza 100 buscas em largura por representação e
grava os resultados em `resultados/experimentos.csv`:

```bash
python experimentos.py grafos/exemplo.txt --repeticoes 100
```

Para escolher outro arquivo de saída:

```bash
python experimentos.py grafos/exemplo.txt \
  --repeticoes 100 \
  --saida resultados/experimentos_grafo1.csv
```

A leitura do grafo é feita antes da medição do tempo; cada chamada da BFS é
cronometrada individualmente e o programa calcula a média. A medição de memória
é feita em um processo separado para cada representação, após carregar o grafo,
consultando o RSS do processo em Linux (`/proc/self/status`). O RSS inclui o
interpretador Python e a biblioteca, e não somente a estrutura do grafo; por
isso, essa medida representa o consumo do processo e pode variar entre
execuções.

O CSV informa a representação, quantidade de vértices e arestas, número de
buscas, número de origens distintas, tempo total, tempo médio por BFS e memória
residente do processo. Se houver menos vértices do que buscas solicitadas, o
programa visita todos os vértices como origem antes de reutilizar as origens.
Consequentemente, o grafo de cinco vértices do exemplo serve para validar o
funcionamento, mas não para uma comparação de desempenho representativa.

Execute todos os testes com:

```bash
python -m unittest -v
```
