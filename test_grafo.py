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


class TestEstatisticasGrafo(unittest.TestCase):
    def test_graus_do_exemplo_em_ambas_representacoes(self) -> None:
        esperados = {1: 2, 2: 2, 3: 1, 4: 1, 5: 4}
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                grafo = criar_grafo(representacao)
                self.assertEqual(grafo.graus(), esperados)

    def test_estatisticas_do_exemplo_em_ambas_representacoes(self) -> None:
        esperadas = {
            "numero_vertices": 5,
            "numero_arestas": 5,
            "grau_minimo": 1,
            "grau_maximo": 4,
            "grau_medio": 2.0,
        }
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                grafo = criar_grafo(representacao)
                self.assertEqual(grafo.estatisticas(), esperadas)
                self.assertEqual(grafo.numero_arestas, 5)
                self.assertEqual(grafo.grau_minimo, 1)
                self.assertEqual(grafo.grau_maximo, 4)
                self.assertEqual(grafo.grau_medio, 2.0)

    def test_vertices_isolados_sao_contabilizados(self) -> None:
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                grafo = Grafo(4, representacao=representacao)
                grafo.adicionar_aresta(1, 2)
                self.assertEqual(grafo.graus(), {1: 1, 2: 1, 3: 0, 4: 0})
                self.assertEqual(grafo.numero_arestas, 1)
                self.assertEqual(grafo.grau_minimo, 0)
                self.assertEqual(grafo.grau_maximo, 1)
                self.assertEqual(grafo.grau_medio, 0.5)

    def test_laco_contribui_duas_unidades_para_o_grau(self) -> None:
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                grafo = Grafo(2, representacao=representacao)
                grafo.adicionar_aresta(1, 1)
                grafo.adicionar_aresta(1, 2)
                self.assertEqual(grafo.graus(), {1: 3, 2: 1})
                self.assertEqual(grafo.numero_arestas, 2)
                self.assertEqual(grafo.grau_medio, 2.0)


class TestBuscaEmLargura(unittest.TestCase):
    def test_bfs_do_exemplo_com_origem_1(self) -> None:
        esperado = {
            1: {"pai": None, "nivel": 0},
            2: {"pai": 1, "nivel": 1},
            3: {"pai": 5, "nivel": 2},
            4: {"pai": 5, "nivel": 2},
            5: {"pai": 1, "nivel": 1},
        }
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                grafo = criar_grafo(representacao)
                self.assertEqual(grafo.busca_em_largura(1), esperado)

    def test_bfs_e_equivalente_nas_duas_representacoes(self) -> None:
        grafo_lista = criar_grafo("lista")
        grafo_matriz = criar_grafo("matriz")
        for origem in range(1, 6):
            with self.subTest(origem=origem):
                self.assertEqual(
                    grafo_lista.busca_em_largura(origem),
                    grafo_matriz.busca_em_largura(origem),
                )

    def test_origem_tem_nivel_zero_e_pai_nulo(self) -> None:
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                resultado = criar_grafo(representacao).busca_em_largura(3)
                self.assertIsNone(resultado[3]["pai"])
                self.assertEqual(resultado[3]["nivel"], 0)

    def test_vertices_inalcancaveis_tem_pai_e_nivel_nulos(self) -> None:
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                grafo = Grafo(4, representacao=representacao)
                grafo.adicionar_aresta(1, 2)
                resultado = grafo.busca_em_largura(1)
                self.assertEqual(resultado[1], {"pai": None, "nivel": 0})
                self.assertEqual(resultado[2], {"pai": 1, "nivel": 1})
                self.assertEqual(resultado[3], {"pai": None, "nivel": None})
                self.assertEqual(resultado[4], {"pai": None, "nivel": None})

    def test_rejeita_origem_fora_do_grafo(self) -> None:
        grafo = criar_grafo("lista")
        with self.assertRaises(ValueError):
            grafo.busca_em_largura(0)
        with self.assertRaises(ValueError):
            grafo.busca_em_largura(6)

    def test_rejeita_origem_que_nao_e_inteira(self) -> None:
        grafo = criar_grafo("lista")
        with self.assertRaises(TypeError):
            grafo.busca_em_largura("1")


if __name__ == "__main__":
    unittest.main()
