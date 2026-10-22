"""Biblioteca para grafos não direcionados, com foco em entradas grandes.

A representação pode ser lista de adjacência ou matriz. A leitura do arquivo
é feita linha a linha; a BFS possui uma versão compacta para evitar criar um
dicionário com milhões de objetos em grafos grandes.
"""

from array import array
from bisect import bisect_left
from collections import deque
from pathlib import Path
import struct
import sys
from typing import Iterable


class Grafo:
    """Armazena um grafo não direcionado por lista ou matriz de adjacência.

    Os vértices são rotulados de 1 até ``numero_vertices``.
    ``representacao`` deve ser ``"lista"`` ou ``"matriz"``.

    Nota: a matriz usa linhas ``bytearray`` (um byte por posição), em vez de
    listas de referências Python. Continua sendo uma matriz de adjacência, mas
    economiza bastante memória. Uma matriz quadrada ainda exige O(V²) bytes.
    """

    def __init__(self, numero_vertices: int, representacao: str = "lista") -> None:
        if not isinstance(numero_vertices, int) or isinstance(numero_vertices, bool):
            raise TypeError("O número de vértices deve ser um inteiro.")
        if numero_vertices < 1:
            raise ValueError("O grafo deve ter pelo menos um vértice.")
        if representacao not in ("lista", "matriz"):
            raise ValueError('A representação deve ser "lista" ou "matriz".')

        self.numero_vertices = numero_vertices
        self.representacao = representacao

        if representacao == "lista":
            self.adjacencia: list[list[int]] | None = [
                [] for _ in range(numero_vertices + 1)
            ]
            self.matriz_adjacencia: list[bytearray] | None = None
        else:
            estimativa = self.estimar_memoria_matriz_bytes(numero_vertices)
            disponivel = self.memoria_disponivel_bytes()
            # Limite absoluto evita tentar alocações enormes mesmo em máquinas
            # com muita RAM. Também preservamos pelo menos metade da memória
            # atualmente disponível. A checagem ocorre antes de criar as linhas.
            limite_absoluto = 4_000_000_000  # 4 GB decimais
            limite_disponivel = (
                int(disponivel * 0.50) if disponivel is not None else 512_000_000
            )
            limite_seguro = min(limite_absoluto, limite_disponivel)
            if estimativa > limite_seguro:
                texto_disponivel = (
                    f"memória atualmente disponível: {disponivel / 1_000_000:.1f} MB. "
                    if disponivel is not None
                    else "memória disponível não pôde ser consultada. "
                )
                raise MemoryError(
                    "A matriz de adjacência foi recusada para evitar falta de memória. "
                    f"Estimativa da matriz: {estimativa / 1_000_000:.1f} MB; "
                    f"limite seguro calculado: {limite_seguro / 1_000_000:.1f} MB; "
                    f"{texto_disponivel}Use a lista de adjacência para este grafo."
                )
            linhas = numero_vertices + 1  # posição zero fica sem uso
            self.adjacencia = None
            self.matriz_adjacencia = [bytearray(linhas) for _ in range(linhas)]

    @staticmethod
    def estimar_memoria_matriz_bytes(numero_vertices: int) -> int:
        """Estima os bytes da matriz de bytearrays, incluindo overhead das linhas.

        A estimativa não inclui o interpretador, as estruturas auxiliares, nem
        a memória necessária para executar outros algoritmos.
        """
        if not isinstance(numero_vertices, int) or isinstance(numero_vertices, bool):
            raise TypeError("O número de vértices deve ser um inteiro.")
        if numero_vertices < 1:
            raise ValueError("O grafo deve ter pelo menos um vértice.")
        linhas = numero_vertices + 1
        ponteiro = struct.calcsize("P")
        overhead_lista = sys.getsizeof([])
        overhead_bytearray = sys.getsizeof(bytearray())
        return (
            overhead_lista + linhas * ponteiro
            + linhas * (overhead_bytearray + linhas)
        )

    @staticmethod
    def memoria_disponivel_bytes() -> int | None:
        """Lê MemAvailable e retorna None se a informação não existir."""
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as arquivo:
                for linha in arquivo:
                    if linha.startswith("MemAvailable:"):
                        kib = int(linha.split()[1])
                        return kib * 1024
        except (OSError, ValueError, IndexError):
            return None
        return None

    @classmethod
    def de_arquivo(
        cls, caminho: str | Path, representacao: str = "lista"
    ) -> "Grafo":
        """Lê o grafo linha a linha para evitar manter o arquivo inteiro na RAM.

        A primeira linha útil contém apenas o número de vértices. Cada linha
        útil restante contém dois inteiros que representam uma aresta. Linhas
        em branco e linhas iniciadas por ``#`` são ignoradas. Arestas repetidas
        são eliminadas e laços são contabilizados corretamente.
        """
        caminho = Path(caminho)
        grafo: Grafo | None = None

        try:
            with caminho.open("r", encoding="utf-8") as arquivo:
                for numero_linha, conteudo in enumerate(arquivo, start=1):
                    conteudo = conteudo.strip()
                    if not conteudo or conteudo.startswith("#"):
                        continue

                    if grafo is None:
                        partes = conteudo.split()
                        if len(partes) != 1:
                            raise ValueError(
                                f"Linha {numero_linha}: informe somente o número de vértices."
                            )
                        try:
                            numero_vertices = int(partes[0])
                        except ValueError as erro:
                            raise ValueError(
                                f"Linha {numero_linha}: número de vértices inválido."
                            ) from erro
                        grafo = cls(numero_vertices, representacao=representacao)
                        continue

                    partes = conteudo.split()
                    if len(partes) != 2:
                        raise ValueError(
                            f"Linha {numero_linha}: cada aresta deve conter exatamente dois vértices."
                        )
                    try:
                        u, v = int(partes[0]), int(partes[1])
                    except ValueError as erro:
                        raise ValueError(
                            f"Linha {numero_linha}: os vértices da aresta devem ser inteiros."
                        ) from erro

                    if not (1 <= u <= grafo.numero_vertices):
                        raise ValueError(
                            f"Linha {numero_linha}: vértice {u} fora do intervalo "
                            f"1..{grafo.numero_vertices}."
                        )
                    if not (1 <= v <= grafo.numero_vertices):
                        raise ValueError(
                            f"Linha {numero_linha}: vértice {v} fora do intervalo "
                            f"1..{grafo.numero_vertices}."
                        )

                    if representacao == "lista":
                        # Inserção O(1) amortizado. Ordenação e remoção de
                        # duplicatas são feitas uma única vez após a leitura.
                        grafo.adjacencia[u].append(v)
                        if u != v:
                            grafo.adjacencia[v].append(u)
                    else:
                        grafo.matriz_adjacencia[u][v] = 1
                        grafo.matriz_adjacencia[v][u] = 1
        except OSError as erro:
            raise OSError(
                f"Não foi possível ler o arquivo '{caminho}': {erro.strerror or erro}."
            ) from erro

        if grafo is None:
            raise ValueError("O arquivo de entrada está vazio.")

        if representacao == "lista":
            # Classifica e deduplica in-place, sem criar uma segunda lista do
            # mesmo tamanho (importante para arquivos com dezenas de milhões
            # de arestas).
            for vertice in range(1, grafo.numero_vertices + 1):
                vizinhos = grafo.adjacencia[vertice]
                if len(vizinhos) < 2:
                    continue
                vizinhos.sort()
                escrita = 1
                for leitura in range(1, len(vizinhos)):
                    if vizinhos[leitura] != vizinhos[escrita - 1]:
                        vizinhos[escrita] = vizinhos[leitura]
                        escrita += 1
                del vizinhos[escrita:]

        return grafo

    def _validar_vertice(self, vertice: int) -> None:
        if not isinstance(vertice, int) or isinstance(vertice, bool):
            raise TypeError("O rótulo do vértice deve ser um inteiro.")
        if not 1 <= vertice <= self.numero_vertices:
            raise ValueError(
                f"Vértice inválido: {vertice}. Use um valor entre 1 e "
                f"{self.numero_vertices}."
            )

    def adicionar_aresta(self, u: int, v: int) -> None:
        """Adiciona uma aresta não direcionada, sem duplicar a mesma conexão."""
        self._validar_vertice(u)
        self._validar_vertice(v)

        if self.representacao == "lista":
            vizinhos_u = self.adjacencia[u]
            posicao_v = bisect_left(vizinhos_u, v)
            if posicao_v >= len(vizinhos_u) or vizinhos_u[posicao_v] != v:
                vizinhos_u.insert(posicao_v, v)

            if u != v:
                vizinhos_v = self.adjacencia[v]
                posicao_u = bisect_left(vizinhos_v, u)
                if posicao_u >= len(vizinhos_v) or vizinhos_v[posicao_u] != u:
                    vizinhos_v.insert(posicao_u, u)
        else:
            self.matriz_adjacencia[u][v] = 1
            self.matriz_adjacencia[v][u] = 1

    def _iterar_vizinhos_matriz(self, vertice: int) -> Iterable[int]:
        """Itera apenas sobre células verdadeiras usando busca em C do bytearray."""
        linha = self.matriz_adjacencia[vertice]
        indice = linha.find(b"\x01", 1)
        while indice != -1:
            yield indice
            indice = linha.find(b"\x01", indice + 1)

    def _iter_vizinhos(self, vertice: int) -> Iterable[int]:
        """Visão interna sem copiar a lista de vizinhos."""
        if self.representacao == "lista":
            return self.adjacencia[vertice]
        return self._iterar_vizinhos_matriz(vertice)

    def vizinhos(self, vertice: int) -> list[int]:
        """Retorna uma nova lista com os vizinhos em ordem crescente."""
        self._validar_vertice(vertice)
        return list(self._iter_vizinhos(vertice))

    def grau(self, vertice: int) -> int:
        """Retorna o grau do vértice; cada laço contribui duas unidades."""
        self._validar_vertice(vertice)
        if self.representacao == "lista":
            vizinhos = self.adjacencia[vertice]
            indice = bisect_left(vizinhos, vertice)
            tem_laco = indice < len(vizinhos) and vizinhos[indice] == vertice
            return len(vizinhos) + int(tem_laco)

        linha = self.matriz_adjacencia[vertice]
        grau = sum(linha[1:])
        if linha[vertice]:
            grau += 1
        return grau

    def graus(self) -> dict[int, int]:
        """Retorna o grau de cada vértice. Em grafos enormes, prefira estatisticas()."""
        return {vertice: self.grau(vertice) for vertice in range(1, self.numero_vertices + 1)}

    @property
    def numero_arestas(self) -> int:
        """Retorna a quantidade de arestas não direcionadas, sem duplicações."""
        soma_graus = 0
        for vertice in range(1, self.numero_vertices + 1):
            soma_graus += self.grau(vertice)
        return soma_graus // 2

    def estatisticas(self) -> dict[str, int | float]:
        """Calcula estatísticas sem criar um dicionário de graus por vértice."""
        grau_minimo: int | None = None
        grau_maximo = 0
        soma_graus = 0
        for vertice in range(1, self.numero_vertices + 1):
            grau = self.grau(vertice)
            if grau_minimo is None or grau < grau_minimo:
                grau_minimo = grau
            if grau > grau_maximo:
                grau_maximo = grau
            soma_graus += grau
        return {
            "numero_vertices": self.numero_vertices,
            "numero_arestas": soma_graus // 2,
            "grau_minimo": grau_minimo if grau_minimo is not None else 0,
            "grau_maximo": grau_maximo,
            "grau_medio": soma_graus / self.numero_vertices,
        }

    @property
    def grau_minimo(self) -> int:
        return int(self.estatisticas()["grau_minimo"])

    @property
    def grau_maximo(self) -> int:
        return int(self.estatisticas()["grau_maximo"])

    @property
    def grau_medio(self) -> float:
        return float(self.estatisticas()["grau_medio"])

    def busca_em_largura_compacta(self, origem: int) -> tuple[array, array]:
        """Executa BFS e devolve arrays compactos (pais, níveis), indexados por rótulo.

        O valor -1 representa pai inexistente ou vértice inalcançável. A origem
        tem pai -1 e nível zero. Essa versão é indicada para grafos grandes.
        """
        self._validar_vertice(origem)

        tipo_array = "i"
        limite_i = (1 << (8 * array("i").itemsize - 1)) - 1
        if self.numero_vertices > limite_i:
            tipo_array = "q"
        pais = array(tipo_array, [-1]) * (self.numero_vertices + 1)
        niveis = array(tipo_array, [-1]) * (self.numero_vertices + 1)
        niveis[origem] = 0
        fila = deque([origem])

        while fila:
            atual = fila.popleft()
            proximo_nivel = niveis[atual] + 1
            for vizinho in self._iter_vizinhos(atual):
                if niveis[vizinho] == -1:
                    pais[vizinho] = atual
                    niveis[vizinho] = proximo_nivel
                    fila.append(vizinho)

        return pais, niveis

    def busca_em_largura(self, origem: int) -> dict[int, dict[str, int | None]]:
        """Executa BFS e retorna pai e nível por vértice como dicionário.

        Para grafos com milhões de vértices, use ``busca_em_largura_compacta``
        para evitar o custo de memória da conversão para dicionários Python.
        """
        pais, niveis = self.busca_em_largura_compacta(origem)
        resultado: dict[int, dict[str, int | None]] = {}
        for vertice in range(1, self.numero_vertices + 1):
            pai = pais[vertice]
            nivel = niveis[vertice]
            resultado[vertice] = {
                "pai": None if pai == -1 else pai,
                "nivel": None if nivel == -1 else nivel,
            }
        return resultado

    def distancia(self, origem: int, destino: int) -> int | None:
        """Retorna a distância em arestas ou None quando não há caminho."""
        self._validar_vertice(destino)
        _, niveis = self.busca_em_largura_compacta(origem)
        nivel = niveis[destino]
        return None if nivel == -1 else int(nivel)
