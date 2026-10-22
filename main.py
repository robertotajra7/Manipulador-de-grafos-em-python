"""Programa principal para leitura de um grafo e gravação de resultados."""

import argparse
from array import array
from pathlib import Path

from grafo import Grafo


def formatar_estatisticas(grafo: Grafo) -> str:
    """Retorna as estatísticas do grafo em formato texto."""
    estatisticas = grafo.estatisticas()
    return (
        "Estatísticas do grafo\n"
        f"Número de vértices: {estatisticas['numero_vertices']}\n"
        f"Número de arestas: {estatisticas['numero_arestas']}\n"
        f"Grau mínimo: {estatisticas['grau_minimo']}\n"
        f"Grau máximo: {estatisticas['grau_maximo']}\n"
        f"Grau médio: {estatisticas['grau_medio']:.2f}\n"
    )


def formatar_resultado_bfs(grafo: Grafo, origem: int) -> str:
    """Formata a árvore BFS em memória; indicada para grafos pequenos."""
    pais, niveis = grafo.busca_em_largura_compacta(origem)
    linhas = [
        "Busca em largura (BFS)",
        f"Vértice de origem: {origem}",
        "",
        "Vértice;Pai;Nível",
    ]
    for vertice in range(1, grafo.numero_vertices + 1):
        pai = pais[vertice]
        nivel = niveis[vertice]
        texto_pai = "-" if pai == -1 else str(pai)
        texto_nivel = "-" if nivel == -1 else str(nivel)
        linhas.append(f"{vertice};{texto_pai};{texto_nivel}")
    return "\n".join(linhas) + "\n"


def escrever_resultado_bfs(
    caminho: str | Path,
    grafo: Grafo,
    origem: int,
    pais: array,
    niveis: array,
) -> None:
    """Grava pais e níveis linha a linha, sem criar uma saída gigante em RAM."""
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8") as arquivo:
        arquivo.write("Busca em largura (BFS)\n")
        arquivo.write(f"Vértice de origem: {origem}\n\n")
        arquivo.write("Vértice;Pai;Nível\n")
        for vertice in range(1, grafo.numero_vertices + 1):
            pai = pais[vertice]
            nivel = niveis[vertice]
            texto_pai = "-" if pai == -1 else str(pai)
            texto_nivel = "-" if nivel == -1 else str(nivel)
            arquivo.write(f"{vertice};{texto_pai};{texto_nivel}\n")


def escrever_arquivo(caminho: str | Path, conteudo: str) -> None:
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo, encoding="utf-8")


def processar_arquivo(
    entrada: str | Path,
    representacao: str,
    origem: int,
    saida_estatisticas: str | Path,
    saida_bfs: str | Path,
) -> None:
    """Lê um grafo, processa estatísticas e BFS e grava os arquivos de saída."""
    grafo = Grafo.de_arquivo(entrada, representacao=representacao)
    # Os arrays compactos deixam a gravação viável para milhões de vértices.
    pais, niveis = grafo.busca_em_largura_compacta(origem)
    escrever_arquivo(saida_estatisticas, formatar_estatisticas(grafo))
    escrever_resultado_bfs(saida_bfs, grafo, origem, pais, niveis)


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Lê um grafo não direcionado e grava as estatísticas e a árvore BFS."
        )
    )
    parser.add_argument("entrada", help="arquivo texto de entrada do grafo")
    parser.add_argument(
        "--representacao", choices=("lista", "matriz"), default="lista",
        help="representação usada (padrão: lista)",
    )
    parser.add_argument("--origem", type=int, default=1, help="origem da BFS (padrão: 1)")
    parser.add_argument(
        "--saida-estatisticas", default="resultados/estatisticas.txt",
        help="caminho do arquivo de estatísticas",
    )
    parser.add_argument(
        "--saida-bfs", default=None,
        help="caminho do arquivo BFS (padrão: resultados/bfs_origem_N.txt)",
    )
    return parser


def main(argumentos: list[str] | None = None) -> int:
    parser = criar_parser()
    args = parser.parse_args(argumentos)
    saida_bfs = args.saida_bfs or f"resultados/bfs_origem_{args.origem}.txt"
    try:
        processar_arquivo(
            entrada=args.entrada,
            representacao=args.representacao,
            origem=args.origem,
            saida_estatisticas=args.saida_estatisticas,
            saida_bfs=saida_bfs,
        )
    except (OSError, TypeError, ValueError, MemoryError) as erro:
        parser.error(str(erro))
    print(f"Estatísticas gravadas em: {args.saida_estatisticas}")
    print(f"Resultado da BFS gravado em: {saida_bfs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
