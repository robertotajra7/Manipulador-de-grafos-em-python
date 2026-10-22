"""Testes da biblioteca: representações, estatísticas e BFS."""
"""Testando testando blablabla"""

import tempfile
import unittest
from pathlib import Path

from grafo import Grafo

ARESTAS_EXEMPLO = [(1, 2), (2, 5), (5, 3), (4, 5), (1, 5)]
VIZINHOS_ESPERADOS = {
    1: [2, 5],
    2: [1, 5],
    3: [5],
    4: [5],
    5: [1, 2, 3, 4],
}


def criar_grafo(representacao: str = "lista") -> Grafo:
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
        for vertice, esperado in VIZINHOS_ESPERADOS.items():
            with self.subTest(vertice=vertice):
                self.assertEqual(self.grafo.vizinhos(vertice), esperado)

    def test_aresta_nao_direcionada(self) -> None:
        self.assertIn(2, self.grafo.vizinhos(1))
        self.assertIn(1, self.grafo.vizinhos(2))

    def test_aresta_repetida_nao_duplica_vizinhos(self) -> None:
        self.grafo.adicionar_aresta(1, 2)
        self.assertEqual(self.grafo.vizinhos(1), [2, 5])
        self.assertEqual(self.grafo.vizinhos(2), [1, 5])

    def test_numero_de_vertices_invalido(self) -> None:
        with self.assertRaises(ValueError):
            Grafo(0)

    def test_vertice_fora_do_intervalo(self) -> None:
        with self.assertRaises(ValueError):
            self.grafo.adicionar_aresta(1, 6)
        with self.assertRaises(ValueError):
            self.grafo.vizinhos(0)


class TestGrafoMatrizAdjacencia(unittest.TestCase):
    def setUp(self) -> None:
        self.grafo = criar_grafo("matriz")

    def test_vizinhos_de_cada_vertice(self) -> None:
        for vertice, esperado in VIZINHOS_ESPERADOS.items():
            with self.subTest(vertice=vertice):
                self.assertEqual(self.grafo.vizinhos(vertice), esperado)

    def test_matriz_e_simetrica(self) -> None:
        matriz = self.grafo.matriz_adjacencia
        for u in range(1, 6):
            for v in range(1, 6):
                self.assertEqual(matriz[u][v], matriz[v][u])

    def test_matriz_utiliza_bytearray_por_linha(self) -> None:
        self.assertIsInstance(self.grafo.matriz_adjacencia[1], bytearray)
        self.assertIsNone(self.grafo.adjacencia)

    def test_aresta_repetida_nao_altera_vizinhos(self) -> None:
        self.grafo.adicionar_aresta(1, 2)
        self.assertEqual(self.grafo.vizinhos(1), [2, 5])
        self.assertEqual(self.grafo.vizinhos(2), [1, 5])

    def test_representacao_desconhecida_e_rejeitada(self) -> None:
        with self.assertRaises(ValueError):
            Grafo(5, representacao="arvore")

    def test_estimativa_de_matriz_cresce_quadraticamente(self) -> None:
        pequeno = Grafo.estimar_memoria_matriz_bytes(1000)
        grande = Grafo.estimar_memoria_matriz_bytes(2000)
        self.assertGreater(grande, pequeno * 3.8)
        self.assertLess(grande, pequeno * 4.2)


class TestEstatisticasGrafo(unittest.TestCase):
    def test_graus_do_exemplo_em_ambas_representacoes(self) -> None:
        esperado = {1: 2, 2: 2, 3: 1, 4: 1, 5: 4}
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                self.assertEqual(criar_grafo(representacao).graus(), esperado)

    def test_estatisticas_do_exemplo(self) -> None:
        esperado = {
            "numero_vertices": 5, "numero_arestas": 5,
            "grau_minimo": 1, "grau_maximo": 4, "grau_medio": 2.0,
        }
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                grafo = criar_grafo(representacao)
                self.assertEqual(grafo.estatisticas(), esperado)
                self.assertEqual(grafo.numero_arestas, 5)

    def test_vertices_isolados(self) -> None:
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                grafo = Grafo(4, representacao=representacao)
                grafo.adicionar_aresta(1, 2)
                self.assertEqual(grafo.graus(), {1: 1, 2: 1, 3: 0, 4: 0})
                self.assertEqual(grafo.estatisticas()["grau_minimo"], 0)
                self.assertEqual(grafo.numero_arestas, 1)

    def test_laco_contribui_duas_unidades_para_o_grau(self) -> None:
        for representacao in ("lista", "matriz"):
            with self.subTest(representacao=representacao):
                grafo = Grafo(2, representacao=representacao)
                grafo.adicionar_aresta(1, 1)
                grafo.adicionar_aresta(1, 2)
                self.assertEqual(grafo.graus(), {1: 3, 2: 1})
                self.assertEqual(grafo.numero_arestas, 2)


class TestBuscaEmLargura(unittest.TestCase):
    def test_bfs_exemplo_origem_1(self) -> None:
        esperado = {
            1: {"pai": None, "nivel": 0},
            2: {"pai": 1, "nivel": 1},
            3: {"pai": 5, "nivel": 2},
            4: {"pai": 5, "nivel": 2},
            5: {"pai": 1, "nivel": 1},
        }
        for representacao in ("lista", "matriz"):
            self.assertEqual(criar_grafo(representacao).busca_em_largura(1), esperado)

    def test_bfs_equivalente_nas_representacoes(self) -> None:
        lista, matriz = criar_grafo("lista"), criar_grafo("matriz")
        for origem in range(1, 6):
            self.assertEqual(lista.busca_em_largura(origem), matriz.busca_em_largura(origem))

    def test_origem_nivel_zero_sem_pai(self) -> None:
        resultado = criar_grafo().busca_em_largura(3)
        self.assertEqual(resultado[3], {"pai": None, "nivel": 0})

    def test_desconexo_retorna_nivel_none(self) -> None:
        grafo = Grafo(4)
        grafo.adicionar_aresta(1, 2)
        resultado = grafo.busca_em_largura(1)
        self.assertEqual(resultado[2], {"pai": 1, "nivel": 1})
        self.assertEqual(resultado[3], {"pai": None, "nivel": None})

    def test_origem_invalida(self) -> None:
        with self.assertRaises(ValueError):
            criar_grafo().busca_em_largura(6)
        with self.assertRaises(TypeError):
            criar_grafo().busca_em_largura("1")

    def test_bfs_compacta_usa_menos_estruturas(self) -> None:
        pais, niveis = criar_grafo().busca_em_largura_compacta(1)
        self.assertEqual(pais[1], -1)
        self.assertEqual(niveis[1], 0)
        self.assertEqual(pais[3], 5)
        self.assertEqual(niveis[3], 2)

    def test_distancia_em_grafo_conexo_e_desconexo(self) -> None:
        self.assertEqual(criar_grafo().distancia(1, 3), 2)
        grafo = Grafo(3)
        grafo.adicionar_aresta(1, 2)
        self.assertIsNone(grafo.distancia(1, 3))


class TestLeituraEEntradaGrande(unittest.TestCase):
    def test_leitura_deduplica_arestas_e_lacos(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "grafo.txt"
            caminho.write_text("3\n1 2\n2 1\n1 1\n1 1\n", encoding="utf-8")
            grafo = Grafo.de_arquivo(caminho, "lista")
            self.assertEqual(grafo.vizinhos(1), [1, 2])
            self.assertEqual(grafo.vizinhos(2), [1])
            self.assertEqual(grafo.grau(1), 3)
            self.assertEqual(grafo.numero_arestas, 2)

    def test_leitura_streaming_com_comentarios(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "grafo.txt"
            caminho.write_text("# teste\n\n3\n1 2\n2 3\n", encoding="utf-8")
            grafo = Grafo.de_arquivo(caminho)
            self.assertEqual(grafo.numero_vertices, 3)
            self.assertEqual(grafo.numero_arestas, 2)

    def test_leitura_rejeita_arquivo_vazio(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "grafo.txt"
            caminho.write_text("\n# sem conteúdo\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "vazio"):
                Grafo.de_arquivo(caminho)

    def test_leitura_rejeita_aresta_invalida(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "grafo.txt"
            caminho.write_text("3\n1 4\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fora do intervalo"):
                Grafo.de_arquivo(caminho)
