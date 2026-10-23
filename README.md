# Estruturas de Dados II

Biblioteca de grafos não direcionados em Python, desenvolvida incrementalmente para a disciplina Estruturas de Dados II.

## Arquivos

- `grafo.py`: biblioteca reutilizável, representações por lista e matriz de adjacência, estatísticas, leitura linha a linha e BFS.
- `main.py`: programa que lê um grafo e gera os arquivos de estatísticas e da árvore BFS.
- `experimentos.py`: compara tempo de BFS e memória residente das representações, registrando resultados em CSV.
- `test_grafo.py`, `test_io.py` e `test_experimentos.py`: testes automatizados.
- `grafos/exemplo.txt`: grafo pequeno para validação durante o desenvolvimento.
- `relatorio_tecnico_final`: relatório completo dol trabalho.

## Formato de entrada

A primeira linha útil contém o número de vértices `n`. Cada linha seguinte contém uma aresta não direcionada `u v`. Vértices são numerados de 1 até `n`. Linhas vazias e linhas iniciadas com `#` são ignoradas.

## Leitura e programa principal

A leitura é feita linha a linha, sem carregar o arquivo completo em memória:

```bash
python main.py grafos/exemplo.txt --representacao lista --origem 1
```

O programa grava `resultados/estatisticas.txt` e `resultados/bfs_origem_1.txt`. A gravação da árvore BFS também é feita linha a linha para evitar manter milhões de linhas numa string em memória.

Para mudar a representação e os caminhos de saída:

```bash
python main.py grafos/exemplo.txt \
  --representacao matriz \
  --origem 3 \
  --saida-estatisticas resultados/estatisticas_matriz.txt \
  --saida-bfs resultados/bfs_matriz_origem_3.txt
```

## Representações e memória

A lista de adjacência armazena vizinhos e é a opção recomendada para grafos grandes. A matriz de adjacência usa linhas `bytearray`, com um byte por posição, em vez de listas de referências Python. Apesar da redução de memória, uma matriz continua tendo custo O(V²). Antes de alocar, a biblioteca estima o consumo e recusa matrizes que excedam 4 GB ou metade da memória disponível (o limite que for menor). Se não for possível consultar a memória disponível, aplica um limite conservador de 512 MB. Isso evita provocar falta de memória no sistema. A estimativa é aproximada e se refere principalmente ao armazenamento da matriz.

Para consultar a estimativa de uma matriz, sem alocá-la:

```bash
python -c 'from grafo import Grafo; print(Grafo.estimar_memoria_matriz_bytes(10000) / 1_000_000, "MB")'
```

## Busca em largura (BFS)

`busca_em_largura(origem)` retorna um dicionário com `pai` e `nivel` para cada vértice, adequado a grafos pequenos e médios. Para grafos com milhões de vértices, use `busca_em_largura_compacta(origem)`, que retorna dois arrays compactos (`pais`, `niveis`) indexados pelo rótulo do vértice. O valor `-1` representa pai inexistente ou nível inalcançável; a origem tem pai `-1` e nível zero.

## Experimentos de tempo e memória

```bash
python experimentos.py grafos/exemplo.txt --repeticoes 100 --saida resultados/experimentos_exemplo.csv
```

O padrão é 100 buscas BFS por representação. As mesmas origens (escolhidas de forma reproduzível) são utilizadas nas duas representações. A leitura é feita fora da região cronometrada. O tempo inclui a execução compacta da BFS e a criação dos arrays de pais e níveis, mas não a leitura do arquivo nem a gravação no disco. A medição de memória é o RSS do processo depois de carregar o grafo, em um processo separado.

A matriz é avaliada antes da alocação. Se a estimativa ultrapassar 4 GB, metade da memória disponível (o que for menor), ou o limite conservador de 512 MB quando a memória disponível não puder ser consultada, a medição da matriz é marcada como `não executada` no CSV e o motivo é registrado. Isso é esperado para grafos muito grandes; o consumo quadrático torna a matriz fisicamente impraticável em tais escalas.

Os tempos do grafo de cinco vértices são somente uma validação da ferramenta. Para conclusões de desempenho, utilize os grafos disponibilizados pelo professor e registre as limitações de viabilidade da matriz no relatório.

## Estudos de caso: pais e distâncias

O script `estudos_caso.py` resolve as perguntas específicas do enunciado. Ele
carrega cada grafo uma vez usando lista de adjacência e executa cinco BFS
compactas:

- origens 1, 2 e 3: registra os pais dos vértices 10, 20 e 30;
- origem 10: obtém as distâncias para 20 e 30;
- origem 20: obtém a distância para 30.

Como os grafos são não direcionados, as distâncias são simétricas. Os arrays
compactos são liberados entre as buscas para limitar o uso de memória. Se um
vértice não for alcançável, o CSV registra `inalcancavel`.

Execute um grafo por vez para evitar manter mais de um grafo grande na memória:

```bash
python estudos_caso.py ~/Documentos/grafos-edii/grafo_1.txt \
  --saida ~/Documentos/resultados-edii/estudo_caso_grafo_1.csv
```

Repita para `grafo_2.txt` até `grafo_6.txt`, alterando a entrada e o nome da
saída. O CSV gerado contém uma linha por grafo e todas as respostas às perguntas
sobre pais e distâncias. Os arquivos de grafos grandes devem permanecer fora do
repositório Git para evitar sobrecarga.
