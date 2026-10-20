"""Representação básica de um grafo não direcionado.

A classe permite escolher entre lista e matriz de adjacência no momento da
criação. As operações públicas são as mesmas para as duas representações.
"""


class Grafo:
    """Armazena um grafo não direcionado por lista ou matriz de adjacência.

    Os vértices são numerados de 1 até o número informado na criação.

    Args:
        numero_vertices: quantidade de vértices do grafo.
        representacao: "lista" (padrão) ou "matriz".
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

        # Apenas a estrutura escolhida é alocada, permitindo comparar memória.
        if representacao == "lista":
            self.adjacencia: list[list[int]] | None = [
                [] for _ in range(numero_vertices + 1)
            ]
            self.matriz_adjacencia: list[list[bool]] | None = None
        else:
            self.adjacencia = None
            self.matriz_adjacencia = [
                [False] * (numero_vertices + 1)
                for _ in range(numero_vertices + 1)
            ]

    def _validar_vertice(self, vertice: int) -> None:
        """Garante que o vértice informado pertence ao grafo."""
        if not isinstance(vertice, int) or isinstance(vertice, bool):
            raise TypeError("O rótulo do vértice deve ser um inteiro.")
        if not 1 <= vertice <= self.numero_vertices:
            raise ValueError(
                f"Vértice inválido: {vertice}. Use um valor entre 1 e "
                f"{self.numero_vertices}."
            )

    def adicionar_aresta(self, u: int, v: int) -> None:
        """Adiciona a aresta não direcionada entre u e v.

        A aresta fica registrada nos dois sentidos. A mesma aresta não é
        adicionada novamente se já estiver presente.
        """
        self._validar_vertice(u)
        self._validar_vertice(v)

        if self.representacao == "lista":
            # A lista contém cada vizinho uma única vez, inclusive em um laço.
            if v not in self.adjacencia[u]:
                self.adjacencia[u].append(v)
                self.adjacencia[u].sort()
            if u not in self.adjacencia[v]:
                self.adjacencia[v].append(u)
                self.adjacencia[v].sort()
        else:
            self.matriz_adjacencia[u][v] = True
            self.matriz_adjacencia[v][u] = True

    def vizinhos(self, vertice: int) -> list[int]:
        """Retorna uma lista ordenada dos vizinhos do vértice informado."""
        self._validar_vertice(vertice)

        if self.representacao == "lista":
            return self.adjacencia[vertice].copy()

        return [
            vizinho
            for vizinho in range(1, self.numero_vertices + 1)
            if self.matriz_adjacencia[vertice][vizinho]
        ]

    def grau(self, vertice: int) -> int:
        """Retorna o grau do vértice informado.

        Em um grafo não direcionado, um laço (aresta de um vértice para ele
        mesmo) contribui com duas unidades para o grau.
        """
        vizinhos = self.vizinhos(vertice)
        grau = len(vizinhos)

        # Um laço aparece uma vez na representação, mas conta duas vezes no grau.
        if vertice in vizinhos:
            grau += 1

        return grau

    def graus(self) -> dict[int, int]:
        """Retorna um dicionário com o grau de cada vértice."""
        return {
            vertice: self.grau(vertice)
            for vertice in range(1, self.numero_vertices + 1)
        }

    @property
    def numero_arestas(self) -> int:
        """Retorna a quantidade de arestas do grafo, sem duplicar arestas.

        Para grafos não direcionados, a soma dos graus é duas vezes o número
        de arestas. Essa relação também funciona para grafos com laços.
        """
        return sum(self.graus().values()) // 2

    @property
    def grau_minimo(self) -> int:
        """Retorna o menor grau entre os vértices do grafo."""
        return min(self.graus().values())

    @property
    def grau_maximo(self) -> int:
        """Retorna o maior grau entre os vértices do grafo."""
        return max(self.graus().values())

    @property
    def grau_medio(self) -> float:
        """Retorna o grau médio dos vértices do grafo."""
        return sum(self.graus().values()) / self.numero_vertices

    def estatisticas(self) -> dict[str, int | float]:
        """Retorna as estatísticas solicitadas no trabalho.

        As chaves do dicionário são: numero_vertices, numero_arestas,
        grau_minimo, grau_maximo e grau_medio.
        """
        graus = self.graus()
        return {
            "numero_vertices": self.numero_vertices,
            "numero_arestas": sum(graus.values()) // 2,
            "grau_minimo": min(graus.values()),
            "grau_maximo": max(graus.values()),
            "grau_medio": sum(graus.values()) / self.numero_vertices,
        }
