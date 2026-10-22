"""Resolve as perguntas de BFS e distância dos estudos de caso da disciplina.

Para cada grafo, executa cinco BFS compactas: origens 1, 2 e 3 para consultar
os pais dos vértices 10, 20 e 30; origens 10 e 20 para calcular as três
 distâncias pedidas. O grafo é carregado uma vez e os arquivos de saída são
escritos somente depois dos cálculos.
"""

import argparse
import csv
from pathlib import Path
from typing import Any

from grafo import Grafo

ORIGENS_PAIS = (1, 2, 3)
ALVOS = (10, 20, 30)
CAMPOS_CSV = [
    "grafo",
    "numero_vertices",
    "numero_arestas",
    "pai_10_bfs_origem_1",
    "pai_20_bfs_origem_1",
    "pai_30_bfs_origem_1",
    "pai_10_bfs_origem_2",
    "pai_20_bfs_origem_2",
    "pai_30_bfs_origem_2",
    "pai_10_bfs_origem_3",
    "pai_20_bfs_origem_3",
    "pai_30_bfs_origem_3",
    "distancia_10_20",
    "distancia_10_30",
    "distancia_20_30",
]


def formatar_vertice(valor: int) -> int | str:
    """Converte o marcador -1 da BFS para um valor legível no CSV."""
    return "inalcancavel" if valor == -1 else valor


def processar_grafo(caminho: str | Path) -> dict[str, Any]:
    """Calcula pais e distâncias pedidos para um único grafo não direcionado."""
    caminho = Path(caminho)
    grafo = Grafo.de_arquivo(caminho, representacao="lista")
    if grafo.numero_vertices < max(ALVOS):
        raise ValueError(
            f"O grafo '{caminho}' tem {grafo.numero_vertices} vértices; "
            "as consultas exigem pelo menos 30 vértices."
        )

    estatisticas = grafo.estatisticas()
    resultado: dict[str, Any] = {
        "grafo": caminho.name,
        "numero_vertices": estatisticas["numero_vertices"],
        "numero_arestas": estatisticas["numero_arestas"],
    }

    # Três BFS para consultar os pais de 10, 20 e 30 a partir de 1, 2 e 3.
    for origem in ORIGENS_PAIS:
        print(f"  BFS de origem {origem} para consultar os pais de {ALVOS}...", flush=True)
        pais, niveis = grafo.busca_em_largura_compacta(origem)
        for alvo in ALVOS:
            resultado[f"pai_{alvo}_bfs_origem_{origem}"] = formatar_vertice(pais[alvo])
        del pais, niveis

    # BFS da origem 10 fornece as distâncias 10-20 e 10-30.
    print("  BFS de origem 10 para as distâncias...", flush=True)
    pais, niveis_de_10 = grafo.busca_em_largura_compacta(10)
    resultado["distancia_10_20"] = formatar_vertice(niveis_de_10[20])
    resultado["distancia_10_30"] = formatar_vertice(niveis_de_10[30])
    del pais, niveis_de_10

    # Como o grafo é não direcionado, a BFS de 20 fornece a distância 20-30.
    print("  BFS de origem 20 para a distância restante...", flush=True)
    pais, niveis_de_20 = grafo.busca_em_largura_compacta(20)
    resultado["distancia_20_30"] = formatar_vertice(niveis_de_20[30])
    del pais, niveis_de_20, grafo
    return resultado


def gravar_csv(resultado: dict[str, Any], caminho_saida: str | Path) -> None:
    """Grava os resultados de um grafo em um CSV de uma linha."""
    destino = Path(caminho_saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV)
        escritor.writeheader()
        escritor.writerow(resultado)


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Calcula os pais dos vértices 10, 20 e 30 para BFS com origens "
            "1, 2 e 3, além das distâncias entre (10,20), (10,30) e (20,30)."
        )
    )
    parser.add_argument("entrada", help="caminho para o arquivo .txt do grafo")
    parser.add_argument(
        "--saida",
        default=None,
        help="caminho do CSV de saída (padrão: resultados/estudo_caso_<grafo>.csv)",
    )
    return parser


def main(argumentos: list[str] | None = None) -> int:
    parser = criar_parser()
    args = parser.parse_args(argumentos)
    entrada = Path(args.entrada)
    saida = Path(args.saida) if args.saida else Path("resultados") / f"estudo_caso_{entrada.stem}.csv"

    try:
        print(f"Carregando {entrada} como lista de adjacência...", flush=True)
        resultado = processar_grafo(entrada)
        gravar_csv(resultado, saida)
    except (OSError, TypeError, ValueError, MemoryError) as erro:
        parser.error(str(erro))

    print("\nResultados do estudo de caso")
    print(f"Grafo: {resultado['grafo']}")
    print(f"Vértices: {resultado['numero_vertices']}")
    print(f"Arestas distintas: {resultado['numero_arestas']}")
    print("\nPais dos vértices (pai '-' significa inalcançável):")
    for origem in ORIGENS_PAIS:
        pais = ", ".join(
            f"pai({alvo})={resultado[f'pai_{alvo}_bfs_origem_{origem}']}"
            for alvo in ALVOS
        )
        print(f"  BFS origem {origem}: {pais}")
    print("\nDistâncias (inalcancavel significa que não existe caminho):")
    for par in ((10, 20), (10, 30), (20, 30)):
        print(f"  d({par[0]},{par[1]}) = {resultado[f'distancia_{par[0]}_{par[1]}']}")
    print(f"\nCSV gravado em: {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
