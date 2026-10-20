"""Compara tempo de BFS e memória residente das representações do grafo.

A leitura dos grafos e a escrita do CSV ocorrem fora da cronometragem da BFS.
A medição de memória é feita em processos separados para que o pico/resíduo de
uma representação não contamine a medição da outra.
"""

import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path

from grafo import Grafo

REPRESENTACOES = ("lista", "matriz")
CAMPOS_CSV = (
    "representacao",
    "numero_vertices",
    "numero_arestas",
    "repeticoes",
    "origens_distintas",
    "tempo_total_ms",
    "tempo_medio_ms",
    "memoria_residente_mb",
)


def inteiro_positivo(texto: str) -> int:
    """Converte um argumento em inteiro positivo para o argparse."""
    try:
        valor = int(texto)
    except ValueError as erro:
        raise argparse.ArgumentTypeError("informe um número inteiro") from erro
    if valor < 1:
        raise argparse.ArgumentTypeError("o valor deve ser maior que zero")
    return valor


def gerar_origens(numero_vertices: int, repeticoes: int) -> list[int]:
    """Gera origens diferentes antes de reutilizá-las, se necessário.

    Quando há pelo menos ``repeticoes`` vértices, todas as origens são
    diferentes. Em grafos menores, todos os vértices são usados antes de
    começar novamente pelo vértice 1.
    """
    if numero_vertices < 1:
        raise ValueError("O grafo deve ter pelo menos um vértice.")
    if repeticoes < 1:
        raise ValueError("O número de repetições deve ser positivo.")
    return [(indice % numero_vertices) + 1 for indice in range(repeticoes)]


def medir_tempo_bfs(grafo: Grafo, origens: list[int]) -> tuple[float, float]:
    """Retorna (tempo total em ms, média em ms) das buscas BFS.

    A leitura do grafo, a preparação das origens e a escrita de arquivos não
    são incluídas. Cada chamada da BFS é cronometrada individualmente.
    """
    if not origens:
        raise ValueError("É necessário fornecer pelo menos uma origem.")

    duracoes_ns: list[int] = []
    for origem in origens:
        inicio = time.perf_counter_ns()
        grafo.busca_em_largura(origem)
        duracoes_ns.append(time.perf_counter_ns() - inicio)

    tempo_total_ms = sum(duracoes_ns) / 1_000_000
    tempo_medio_ms = tempo_total_ms / len(duracoes_ns)
    return tempo_total_ms, tempo_medio_ms


def memoria_residente_processo_mb() -> float:
    """Obtém o RSS atual do processo em MB decimais no Linux (via /proc)."""
    caminho_status = Path("/proc/self/status")
    try:
        linhas = caminho_status.read_text(encoding="utf-8").splitlines()
    except OSError as erro:
        raise RuntimeError(
            "A medição automática de memória requer Linux com /proc/self/status."
        ) from erro

    for linha in linhas:
        if linha.startswith("VmRSS:"):
            # O valor de VmRSS é informado em KiB; convertemos para MB decimais.
            memoria_kib = int(linha.split()[1])
            return memoria_kib * 1024 / 1_000_000

    raise RuntimeError("Não foi possível encontrar VmRSS em /proc/self/status.")


def medir_memoria_processo_mb(caminho_entrada: str | Path, representacao: str) -> float:
    """Carrega um grafo em processo separado e mede seu RSS após a leitura."""
    script = Path(__file__).resolve()
    comando = [
        sys.executable,
        str(script),
        "--_memoria-worker",
        str(caminho_entrada),
        representacao,
    ]
    processo = subprocess.run(
        comando,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return float(processo.stdout.strip())


def executar_experimentos(
    caminho_entrada: str | Path,
    repeticoes: int = 100,
    caminho_saida: str | Path = "resultados/experimentos.csv",
) -> list[dict[str, int | float | str]]:
    """Executa as medições para lista e matriz e grava os resultados em CSV."""
    if repeticoes < 1:
        raise ValueError("O número de repetições deve ser positivo.")

    caminho_entrada = Path(caminho_entrada)
    # As medições de RSS usam processos diferentes, isolando uma representação
    # da outra. A leitura do arquivo ocorre antes da leitura de VmRSS.
    memorias = {
        representacao: medir_memoria_processo_mb(caminho_entrada, representacao)
        for representacao in REPRESENTACOES
    }

    resultados: list[dict[str, int | float | str]] = []
    origens: list[int] | None = None

    for representacao in REPRESENTACOES:
        # O carregamento do arquivo ocorre antes de iniciar o cronômetro.
        grafo = Grafo.de_arquivo(caminho_entrada, representacao=representacao)
        if origens is None:
            origens = gerar_origens(grafo.numero_vertices, repeticoes)

        tempo_total_ms, tempo_medio_ms = medir_tempo_bfs(grafo, origens)
        estatisticas = grafo.estatisticas()
        resultados.append(
            {
                "representacao": representacao,
                "numero_vertices": int(estatisticas["numero_vertices"]),
                "numero_arestas": int(estatisticas["numero_arestas"]),
                "repeticoes": repeticoes,
                "origens_distintas": len(set(origens)),
                "tempo_total_ms": round(tempo_total_ms, 6),
                "tempo_medio_ms": round(tempo_medio_ms, 6),
                "memoria_residente_mb": round(memorias[representacao], 3),
            }
        )

    destino = Path(caminho_saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=CAMPOS_CSV)
        escritor.writeheader()
        escritor.writerows(resultados)

    return resultados


def imprimir_resultados(resultados: list[dict[str, int | float | str]]) -> None:
    """Exibe uma tabela resumida dos experimentos."""
    cabecalho = (
        f"{'Representação':<16} {'Vértices':>9} {'Arestas':>8} "
        f"{'Buscas':>7} {'Origens':>8} {'Média (ms)':>12} {'RSS (MB)':>10}"
    )
    print(cabecalho)
    print("-" * len(cabecalho))
    for linha in resultados:
        print(
            f"{linha['representacao']:<16} "
            f"{linha['numero_vertices']:>9} "
            f"{linha['numero_arestas']:>8} "
            f"{linha['repeticoes']:>7} "
            f"{linha['origens_distintas']:>8} "
            f"{linha['tempo_medio_ms']:>12.6f} "
            f"{linha['memoria_residente_mb']:>10.3f}"
        )


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compara a memória residente e o tempo médio de busca em largura "
            "nas representações por lista e matriz de adjacência."
        )
    )
    parser.add_argument("entrada", help="arquivo de entrada do grafo")
    parser.add_argument(
        "--repeticoes",
        type=inteiro_positivo,
        default=100,
        help="quantidade de buscas BFS por representação (padrão: 100)",
    )
    parser.add_argument(
        "--saida",
        default="resultados/experimentos.csv",
        help="caminho do CSV com os resultados",
    )
    return parser


def executar_worker_memoria(caminho: str, representacao: str) -> int:
    """Modo interno: carrega um único grafo e imprime apenas seu RSS."""
    # Mantém uma referência viva ao grafo até depois de ler o RSS.
    grafo = Grafo.de_arquivo(caminho, representacao=representacao)
    print(f"{memoria_residente_processo_mb():.6f}")
    return 0


def main(argumentos: list[str] | None = None) -> int:
    argumentos = list(sys.argv[1:] if argumentos is None else argumentos)
    if (
        len(argumentos) == 3
        and argumentos[0] == "--_memoria-worker"
        and argumentos[2] in REPRESENTACOES
    ):
        try:
            return executar_worker_memoria(argumentos[1], argumentos[2])
        except (OSError, TypeError, ValueError, RuntimeError) as erro:
            print(str(erro), file=sys.stderr)
            return 2

    parser = criar_parser()
    args = parser.parse_args(argumentos)
    try:
        resultados = executar_experimentos(
            args.entrada,
            repeticoes=args.repeticoes,
            caminho_saida=args.saida,
        )
    except (OSError, TypeError, ValueError, RuntimeError, subprocess.SubprocessError) as erro:
        parser.error(str(erro))

    numero_vertices = int(resultados[0]["numero_vertices"])
    if numero_vertices < args.repeticoes:
        print(
            "Aviso: o grafo tem menos vértices do que buscas solicitadas. "
            "Todas as origens serão usadas antes de começar a repeti-las."
        )
    imprimir_resultados(resultados)
    print(f"Resultados detalhados gravados em: {args.saida}")
    print(
        "Nota: o RSS inclui o consumo do interpretador Python e da biblioteca; "
        "a leitura do grafo é feita antes da medição de memória."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
