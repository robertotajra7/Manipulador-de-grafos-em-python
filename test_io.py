"""Testes da leitura do arquivo e das saídas escritas pelo programa principal."""

import tempfile
import unittest
from pathlib import Path

from grafo import Grafo
from main import formatar_estatisticas, formatar_resultado_bfs, processar_arquivo

ARESTAS_EXEMPLO = [(1, 2), (2, 5), (5, 3), (4, 5), (1, 5)]


class TestLeituraDeArquivo(unittest.TestCase):
    def escrever(self, diretorio: str, conteudo: str) -> Path:
        caminho = Path(diretorio) / "grafo.txt"
        caminho.write_text(conteudo, encoding="utf-8")
        return caminho

    def test_le_grafo_nas_duas_representacoes(self) -> None:
        conteudo = "5\n1 2\n2 5\n5 3\n4 5\n1 5\n"
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever(diretorio, conteudo)
            for representacao in ("lista", "matriz"):
                with self.subTest(representacao=representacao):
                    grafo = Grafo.de_arquivo(caminho, representacao)
                    self.assertEqual(grafo.numero_vertices, 5)
                    self.assertEqual(grafo.numero_arestas, 5)
                    self.assertEqual(grafo.vizinhos(5), [1, 2, 3, 4])

    def test_rejeita_numero_de_vertices_nao_inteiro(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever(diretorio, "cinco\n1 2\n")
            with self.assertRaisesRegex(ValueError, "número de vértices inválido"):
                Grafo.de_arquivo(caminho)

    def test_rejeita_aresta_com_formato_incorreto(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever(diretorio, "3\n1 2 3\n")
            with self.assertRaisesRegex(ValueError, "exatamente dois vértices"):
                Grafo.de_arquivo(caminho)

    def test_rejeita_vertice_nao_inteiro(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever(diretorio, "3\n1 x\n")
            with self.assertRaisesRegex(ValueError, "devem ser inteiros"):
                Grafo.de_arquivo(caminho)

    def test_rejeita_arquivo_inexistente(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            with self.assertRaises(OSError):
                Grafo.de_arquivo(Path(diretorio) / "ausente.txt")


class TestArquivosDeSaida(unittest.TestCase):
    def criar_grafo(self) -> Grafo:
        grafo = Grafo(5)
        for u, v in ARESTAS_EXEMPLO:
            grafo.adicionar_aresta(u, v)
        return grafo

    def test_formata_estatisticas(self) -> None:
        esperado = (
            "Estatísticas do grafo\nNúmero de vértices: 5\nNúmero de arestas: 5\n"
            "Grau mínimo: 1\nGrau máximo: 4\nGrau médio: 2.00\n"
        )
        self.assertEqual(formatar_estatisticas(self.criar_grafo()), esperado)

    def test_formata_resultado_bfs(self) -> None:
        texto = formatar_resultado_bfs(self.criar_grafo(), 1)
        self.assertIn("Vértice;Pai;Nível\n", texto)
        self.assertIn("1;-;0\n", texto)
        self.assertIn("3;5;2\n", texto)

    def test_processa_entrada_e_cria_pastas(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            entrada = raiz / "entrada.txt"
            entrada.write_text("5\n1 2\n2 5\n5 3\n4 5\n1 5\n", encoding="utf-8")
            estatisticas = raiz / "nova" / "estatisticas.txt"
            bfs = raiz / "outra" / "bfs.txt"
            processar_arquivo(entrada, "matriz", 1, estatisticas, bfs)
            self.assertIn("Número de arestas: 5", estatisticas.read_text(encoding="utf-8"))
            self.assertIn("4;5;2", bfs.read_text(encoding="utf-8"))

    def test_vertices_inalcancaveis_sao_gravados_com_tracos(self) -> None:
        grafo = Grafo(4)
        grafo.adicionar_aresta(1, 2)
        texto = formatar_resultado_bfs(grafo, 1)
        self.assertIn("3;-;-\n", texto)
        self.assertIn("4;-;-\n", texto)

    def test_origem_invalida_rejeitada(self) -> None:
        with self.assertRaises(ValueError):
            formatar_resultado_bfs(self.criar_grafo(), 6)
