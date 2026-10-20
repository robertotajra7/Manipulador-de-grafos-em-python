"""Programa principal para executar os estudos de caso de grafos."""

import argparse
from pathlib import Path

from grafo import Grafo


def formatar_estatisticas(grafo: Grafo) -> str:
    """Retorna as estatísticas em formato de texto para o arquivo de saída."""
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
    """Executa a BFS e formata pai e nível de cada vértice em texto."""
    resultado = grafo.busca_em_largura(origem)
    linhas = [
        "Busca em largura (BFS)",
        f"Vértice de origem: {origem}",
        "",
        "Vértice;Pai;Nível",
    ]

    for vertice, dados in resultado.items():
        pai = "-" if dados["pai"] is None else str(dados["pai"])
        nivel = "-" if dados["nivel"] is None else str(dados["nivel"])
        linhas.append(f"{vertice};{pai};{nivel}")

    return "\n".join(linhas) + "\n"


def escrever_arquivo(caminho: str | Path, conteudo: str) -> None:
    """Cria a pasta de destino, se necessário, e grava texto em UTF-8."""
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
    """Lê o grafo, calcula os resultados e escreve os dois arquivos de saída."""
    grafo = Grafo.de_arquivo(entrada, representacao=representacao)
    # Calcula a BFS antes de gravar arquivos para validar a origem primeiro.
    texto_bfs = formatar_resultado_bfs(grafo, origem)
    texto_estatisticas = formatar_estatisticas(grafo)
    escrever_arquivo(saida_estatisticas, texto_estatisticas)
    escrever_arquivo(saida_bfs, texto_bfs)


def criar_parser() -> argparse.ArgumentParser:
    """Configura os argumentos de linha de comando do programa."""
    parser = argparse.ArgumentParser(
        description=(
            "Lê um grafo não direcionado e grava suas estatísticas e o "
            "resultado da busca em largura (BFS)."
        )
    )
    parser.add_argument(
        "entrada",
        help="caminho do arquivo de entrada do grafo, por exemplo grafos/exemplo.txt",
    )
    parser.add_argument(
        "--representacao",
        choices=("lista", "matriz"),
        default="lista",
        help="representação utilizada para armazenar o grafo (padrão: lista)",
    )
    parser.add_argument(
        "--origem",
        type=int,
        default=1,
        help="vértice inicial da BFS (padrão: 1)",
    )
    parser.add_argument(
        "--saida-estatisticas",
        default="resultados/estatisticas.txt",
        help="caminho do arquivo de estatísticas",
    )
    parser.add_argument(
        "--saida-bfs",
        default=None,
        help="caminho do arquivo BFS (padrão: resultados/bfs_origem_N.txt)",
    )
    return parser


def main() -> int:
    """Ponto de entrada para execução pelo terminal."""
    parser = criar_parser()
    argumentos = parser.parse_args()
    saida_bfs = argumentos.saida_bfs or f"resultados/bfs_origem_{argumentos.origem}.txt"

    try:
        processar_arquivo(
            entrada=argumentos.entrada,
            representacao=argumentos.representacao,
            origem=argumentos.origem,
            saida_estatisticas=argumentos.saida_estatisticas,
            saida_bfs=saida_bfs,
        )
    except (OSError, TypeError, ValueError) as erro:
        parser.error(str(erro))

    print(f"Estatísticas gravadas em: {argumentos.saida_estatisticas}")
    print(f"Resultado da BFS gravado em: {saida_bfs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
