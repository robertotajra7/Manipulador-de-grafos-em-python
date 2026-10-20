"""Representação básica de um grafo não direcionado por lista de adjacência."""


class Grafo:
    """Armazena os vizinhos de cada vértice em uma lista de adjacência.

    Os vértices são numerados de 1 até o número informado na criação do grafo.
    Esta primeira versão implementa somente a representação por lista.
    """

    def __init__(self, numero_vertices: int) -> None:
        if not isinstance(numero_vertices, int) or isinstance(numero_vertices, bool):
            raise TypeError("O número de vértices deve ser um inteiro.")
        if numero_vertices < 1:
            raise ValueError("O grafo deve ter pelo menos um vértice.")

        self.numero_vertices = numero_vertices
        # A posição 0 fica sem uso para que os índices correspondam aos rótulos 1..n.
        self.adjacencia: list[list[int]] = [
            [] for _ in range(numero_vertices + 1)
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

        Uma aresta comum aparece na lista de vizinhos das duas extremidades.
        A mesma aresta não é adicionada novamente se já estiver presente.
        """
        self._validar_vertice(u)
        self._validar_vertice(v)

        if v not in self.adjacencia[u]:
            self.adjacencia[u].append(v)
            self.adjacencia[u].sort()
            # Ao adicionar um laço (u == v), duas entradas representam o
            # efeito desse laço sobre o grau do vértice.
            if u == v:
                self.adjacencia[u].append(v)
                self.adjacencia[u].sort()
            else:
                self.adjacencia[v].append(u)
                self.adjacencia[v].sort()

    def vizinhos(self, vertice: int) -> list[int]:
        """Retorna uma cópia ordenada da lista de vizinhos do vértice."""
        self._validar_vertice(vertice)
        return self.adjacencia[vertice].copy()
