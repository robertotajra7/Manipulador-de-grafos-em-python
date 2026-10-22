"""Compara BFS e memória das representações com proteção contra matrizes enormes."""

import argparse
import csv
import random
import subprocess
import sys
import time
from pathlib import Path

from grafo import Grafo

REPRESENTACOES = ("lista", "matriz")
CAMPOS_CSV = (
    "representacao", "status", "numero_vertices", "numero_arestas",
    "repeticoes", "origens_distintas", "tempo_total_ms", "tempo_medio_ms",
    "memoria_residente_mb", "memoria_matriz_estimada_mb", "observacao",
)


def inteiro_positivo(texto: str) -> int:
    try:
        valor = int(texto)
    except ValueError as erro:
        raise argparse.ArgumentTypeError("informe um número inteiro") from erro
    if valor < 1:
        raise argparse.ArgumentTypeError("o valor deve ser maior que zero")
    return valor


def obter_numero_vertices(caminho: str | Path) -> int:
    """Lê apenas a primeira linha útil, sem carregar o arquivo inteiro."""
    with Path(caminho).open("r", encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = linha.split()
            if len(partes) != 1:
                raise ValueError(
                    f"Linha {numero_linha}: informe somente o número de vértices."
                )
            try:
                n = int(partes[0])
            except ValueError as erro:
                raise ValueError(f"Linha {numero_linha}: número de vértices inválido.") from erro
            if n < 1:
                raise ValueError("O número de vértices deve ser positivo.")
            return n
    raise ValueError("O arquivo de entrada está vazio.")


def gerar_origens(numero_vertices: int, repeticoes: int, semente: int = 42) -> list[int]:
    """Escolhe origens reproduzíveis; só repete depois de usar todas as possíveis."""
    if numero_vertices < 1:
        raise ValueError("O grafo deve ter pelo menos um vértice.")
    if repeticoes < 1:
        raise ValueError("O número de repetições deve ser positivo.")
    rng = random.Random(semente)
    quantidade_distinta = min(numero_vertices, repeticoes)
    escolhidas = rng.sample(range(1, numero_vertices + 1), quantidade_distinta)
    origens = escolhidas[:]
    while len(origens) < repeticoes:
        faltam = repeticoes - len(origens)
        origens.extend(escolhidas[:faltam])
    return origens


def medir_tempo_bfs(grafo: Grafo, origens: list[int]) -> tuple[float, float]:
    """Cronometra só o núcleo BFS (inclui criação dos arrays, exclui I/O)."""
    if not origens:
        raise ValueError("É necessário fornecer pelo menos uma origem.")
    duracoes_ns: list[int] = []
    for origem in origens:
        inicio = time.perf_counter_ns()
        grafo.busca_em_largura_compacta(origem)
        duracoes_ns.append(time.perf_counter_ns() - inicio)
    total_ms = sum(duracoes_ns) / 1_000_000
    return total_ms, total_ms / len(duracoes_ns)


def memoria_residente_processo_mb() -> float:
    """Retorna o RSS do processo no Linux, depois de o grafo ser carregado."""
    try:
        with open("/proc/self/status", "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                if linha.startswith("VmRSS:"):
                    return int(linha.split()[1]) * 1024 / 1_000_000
    except (OSError, ValueError, IndexError) as erro:
        raise RuntimeError("A medição de memória requer Linux com /proc/self/status.") from erro
    raise RuntimeError("Não foi possível encontrar VmRSS em /proc/self/status.")


def avaliar_viabilidade_matriz(
    numero_vertices: int, memoria_disponivel_bytes: int | None = None
) -> tuple[bool, int, str]:
    """Avalia viabilidade antes de tentar alocar a matriz.

    A regra conservadora exige que a matriz estimada use no máximo metade da
    memória disponível. Se não for possível consultar a memória disponível,
    só permite estimativas de até 512 MB.
    """
    estimativa = Grafo.estimar_memoria_matriz_bytes(numero_vertices)
    disponivel = (
        Grafo.memoria_disponivel_bytes()
        if memoria_disponivel_bytes is None else memoria_disponivel_bytes
    )
    estimativa_mb = estimativa / 1_000_000
    limite_absoluto = 4_000_000_000  # 4 GB decimais
    if disponivel is None:
        limite = min(limite_absoluto, 512_000_000)
        segura = estimativa <= limite
        motivo = (
            f"Matriz estimada em {estimativa_mb:.1f} MB; memória disponível não pôde "
            f"ser consultada; limite conservador: {limite / 1_000_000:.1f} MB."
        )
        return segura, estimativa, motivo
    disponivel_mb = disponivel / 1_000_000
    limite = min(limite_absoluto, int(disponivel * 0.50))
    segura = estimativa <= limite
    motivo = (
        f"Matriz estimada em {estimativa_mb:.1f} MB; memória disponível: "
        f"{disponivel_mb:.1f} MB; limite seguro: {limite / 1_000_000:.1f} MB "
        "(máximo de 4 GB e até 50% da memória disponível)."
    )
    return segura, estimativa, motivo


def medir_memoria_processo_mb(caminho_entrada: str | Path, representacao: str) -> float:
    """Abre um processo isolado, carrega apenas uma representação e mede o RSS."""
    script = Path(__file__).resolve()
    processo = subprocess.run(
        [sys.executable, str(script), "--_memoria-worker", str(caminho_entrada), representacao],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return float(processo.stdout.strip())


def executar_worker_memoria(caminho: str, representacao: str) -> int:
    grafo = Grafo.de_arquivo(caminho, representacao=representacao)
    # Mantém referência local ao grafo enquanto registra o RSS.
    _ = grafo.numero_vertices
    print(f"{memoria_residente_processo_mb():.6f}")
    return 0


def _linha_pulada(
    representacao: str, numero_vertices: int, repeticoes: int,
    estimativa_bytes: int | None, motivo: str,
) -> dict[str, int | float | str]:
    return {
        "representacao": representacao,
        "status": "não executada",
        "numero_vertices": numero_vertices,
        "numero_arestas": "",
        "repeticoes": repeticoes,
        "origens_distintas": "",
        "tempo_total_ms": "",
        "tempo_medio_ms": "",
        "memoria_residente_mb": "",
        "memoria_matriz_estimada_mb": (
            round(estimativa_bytes / 1_000_000, 3) if estimativa_bytes is not None else ""
        ),
        "observacao": motivo,
    }


def executar_experimentos(
    caminho_entrada: str | Path,
    repeticoes: int = 100,
    caminho_saida: str | Path = "resultados/experimentos.csv",
    semente: int = 42,
) -> list[dict[str, int | float | str]]:
    """Mede as duas representações quando viáveis e registra também as recusadas."""
    if repeticoes < 1:
        raise ValueError("O número de repetições deve ser positivo.")
    caminho_entrada = Path(caminho_entrada)
    n = obter_numero_vertices(caminho_entrada)
    origens = gerar_origens(n, repeticoes, semente)
    resultados: list[dict[str, int | float | str]] = []

    for representacao in REPRESENTACOES:
        estimativa = None
        if representacao == "matriz":
            viavel, estimativa, motivo = avaliar_viabilidade_matriz(n)
            if not viavel:
                resultados.append(_linha_pulada(representacao, n, repeticoes, estimativa, motivo))
                continue

        try:
            memoria_mb = medir_memoria_processo_mb(caminho_entrada, representacao)
            grafo = Grafo.de_arquivo(caminho_entrada, representacao=representacao)
            total_ms, media_ms = medir_tempo_bfs(grafo, origens)
            estatisticas = grafo.estatisticas()
        except (OSError, ValueError, MemoryError, RuntimeError, subprocess.SubprocessError) as erro:
            if representacao == "matriz":
                resultados.append(
                    _linha_pulada(representacao, n, repeticoes, estimativa,
                                  f"Medição interrompida com segurança: {erro}")
                )
                continue
            raise

        resultados.append({
            "representacao": representacao,
            "status": "ok",
            "numero_vertices": n,
            "numero_arestas": int(estatisticas["numero_arestas"]),
            "repeticoes": repeticoes,
            "origens_distintas": len(set(origens)),
            "tempo_total_ms": round(total_ms, 6),
            "tempo_medio_ms": round(media_ms, 6),
            "memoria_residente_mb": round(memoria_mb, 3),
            "memoria_matriz_estimada_mb": (
                round(estimativa / 1_000_000, 3) if estimativa is not None else ""
            ),
            "observacao": "RSS medido após carregar; cronômetro inclui apenas as chamadas compactas de BFS.",
        })
        del grafo

    destino = Path(caminho_saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=CAMPOS_CSV)
        escritor.writeheader()
        escritor.writerows(resultados)
    return resultados


def imprimir_resultados(resultados: list[dict[str, int | float | str]]) -> None:
    cabecalho = (
        f"{'Representação':<14} {'Status':<14} {'Vértices':>10} {'Arestas':>12} "
        f"{'Média (ms)':>12} {'RSS (MB)':>10} {'Matriz est. (MB)':>17}"
    )
    print(cabecalho)
    print("-" * len(cabecalho))
    for linha in resultados:
        media = linha["tempo_medio_ms"]
        rss = linha["memoria_residente_mb"]
        estimada = linha["memoria_matriz_estimada_mb"]
        print(
            f"{linha['representacao']:<14} {linha['status']:<14} "
            f"{linha['numero_vertices']:>10} {str(linha['numero_arestas']):>12} "
            f"{(f'{float(media):.6f}' if media != '' else '—'):>12} "
            f"{(f'{float(rss):.3f}' if rss != '' else '—'):>10} "
            f"{(f'{float(estimada):.3f}' if estimada != '' else '—'):>17}"
        )
        if linha["observacao"]:
            print(f"  Observação: {linha['observacao']}")


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compara tempo da BFS e memória das representações por lista e matriz."
    )
    parser.add_argument("entrada", help="arquivo de entrada do grafo")
    parser.add_argument("--repeticoes", type=inteiro_positivo, default=100,
                        help="quantidade de BFS por representação (padrão: 100)")
    parser.add_argument("--saida", default="resultados/experimentos.csv",
                        help="caminho do CSV de resultados")
    parser.add_argument("--semente", type=int, default=42,
                        help="semente para escolha reproduzível das origens")
    return parser


def main(argumentos: list[str] | None = None) -> int:
    argumentos = list(sys.argv[1:] if argumentos is None else argumentos)
    if (len(argumentos) == 3 and argumentos[0] == "--_memoria-worker"
            and argumentos[2] in REPRESENTACOES):
        try:
            return executar_worker_memoria(argumentos[1], argumentos[2])
        except (OSError, TypeError, ValueError, MemoryError, RuntimeError) as erro:
            print(str(erro), file=sys.stderr)
            return 2

    parser = criar_parser()
    args = parser.parse_args(argumentos)
    try:
        resultados = executar_experimentos(
            args.entrada, args.repeticoes, args.saida, args.semente
        )
    except (OSError, TypeError, ValueError, MemoryError, RuntimeError, subprocess.SubprocessError) as erro:
        parser.error(str(erro))
    imprimir_resultados(resultados)
    print(f"Resultados detalhados gravados em: {args.saida}")
    print("A medição de RSS inclui Python e estruturas do grafo, não só os dados de adjacência.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
