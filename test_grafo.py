"""Testes iniciais da representação por lista de adjacência."""

import unittest

from grafo import Grafo


class TestGrafoListaAdjacencia(unittest.TestCase):
    def setUp(self) -> None:
        self.grafo = Grafo(5)
        arestas = [(1, 2), (2, 5), (5, 3), (4, 5), (1, 5)]
        for u, v in arestas:
            self.grafo.adicionar_aresta(u, v)

    def test_quantidade_de_vertices(self) -> None:
        self.assertEqual(self.grafo.numero_vertices, 5)

    def test_vizinhos_de_cada_vertice(self) -> None:
        self.assertEqual(self.grafo.vizinhos(1), [2, 5])
        self.assertEqual(self.grafo.vizinhos(2), [1, 5])
        self.assertEqual(self.grafo.vizinhos(3), [5])
        self.assertEqual(self.grafo.vizinhos(4), [5])
        self.assertEqual(self.grafo.vizinhos(5), [1, 2, 3, 4])

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


if __name__ == "__main__":
    unittest.main()
