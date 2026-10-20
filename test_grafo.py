"""Testes das representações por lista e matriz de adjacência."""

import unittest

from grafo import Grafo


ARESTAS_EXEMPLO = [(1, 2), (2, 5), (5, 3), (4, 5), (1, 5)]
VIZINHOS_ESPERADOS = {
    1: [2, 5],
    2: [1, 5],
    3: [5],
    4: [5],
    5: [1, 2, 3, 4],
}


def criar_grafo(representacao: str) -> Grafo:
    """Cria o grafo do PDF usando a representação solicitada."""
    grafo = Grafo(5, representacao=representacao)
    for u, v in ARESTAS_EXEMPLO:
        grafo.adicionar_aresta(u, v)
    return grafo


class TestGrafoListaAdjacencia(unittest.TestCase):
    def setUp(self) -> None:
        self.grafo = criar_grafo("lista")

    def test_quantidade_de_vertices(self) -> None:
        self.assertEqual(self.grafo.numero_vertices, 5)

    def test_vizinhos_de_cada_vertice(self) -> None:
        for vertice, esperados in VIZINHOS_ESPERADOS.items():
            with self.subTest(vertice=vertice):
                self.assertEqual(self.grafo.vizinhos(vertice), esperados)

    def test_aresta_e_nao_direcionada(self) -> None:
        self.assertIn(2, self.grafo.vizinhos(1))
        self.assertIn(1, self.grafo.vizinhos(2))

    def test_aresta_repetida_nao_duplica_vizinhos(self) -> None:
        self.grafo.adicionar_aresta(1, 2)
        self.assertEqual(self.grafo.vizinhos(1), [2, 5])
        self.assertEqual(self.grafo.vizinhos(2), [1, 5])

    def test_rejeita_numero_de_vertices_invalido(self) -> None:
        with self.assertRaises(ValueError):
            Grafo(0)

    def test_rejeita_vertice_fora_do_intervalo(self) -> None:
        with self.assertRaises(ValueError):
            self.grafo.adicionar_aresta(1, 6)
        with self.assertRaises(ValueError):
            self.grafo.vizinhos(0)


class TestGrafoMatrizAdjacencia(unittest.TestCase):
    def setUp(self) -> None:
        self.grafo = criar_grafo("matriz")

    def test_vizinhos_de_cada_vertice(self) -> None:
        for vertice, esperados in VIZINHOS_ESPERADOS.items():
            with self.subTest(vertice=vertice):
                self.assertEqual(self.grafo.vizinhos(vertice), esperados)

    def test_matriz_e_simetrica(self) -> None:
        matriz = self.grafo.matriz_adjacencia
        for u in range(1, 6):
            for v in range(1, 6):
                with self.subTest(u=u, v=v):
                    self.assertEqual(matriz[u][v], matriz[v][u])

    def test_aresta_repetida_nao_altera_vizinhos(self) -> None:
        self.grafo.adicionar_aresta(1, 2)
        self.assertEqual(self.grafo.vizinhos(1), [2, 5])
        self.assertEqual(self.grafo.vizinhos(2), [1, 5])

    def test_apenas_representacao_escolhida_e_alocada(self) -> None:
        self.assertEqual(self.grafo.representacao, "matriz")
        self.assertIsNone(self.grafo.adjacencia)
        self.assertIsNotNone(self.grafo.matriz_adjacencia)

    def test_rejeita_representacao_desconhecida(self) -> None:
        with self.assertRaises(ValueError):
            Grafo(5, representacao="arvore")


if __name__ == "__main__":
    unittest.main()
