"""Testes de leitura de grafos e geração dos arquivos de saída."""

import tempfile
import unittest
from pathlib import Path

from grafo import Grafo
from main import formatar_estatisticas, formatar_resultado_bfs, processar_arquivo


ARESTAS_EXEMPLO = [(1, 2), (2, 5), (5, 3), (4, 5), (1, 5)]


class TestLeituraDeArquivo(unittest.TestCase):
    def escrever_temporario(self, conteudo: str, diretorio: str) -> Path:
        caminho = Path(diretorio) / "grafo.txt"
        caminho.write_text(conteudo, encoding="utf-8")
        return caminho

    def test_le_grafo_de_arquivo_nas_duas_representacoes(self) -> None:
        conteudo = "5\n1 2\n2 5\n5 3\n4 5\n1 5\n"
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever_temporario(conteudo, diretorio)
            for representacao in ("lista", "matriz"):
                with self.subTest(representacao=representacao):
                    grafo = Grafo.de_arquivo(caminho, representacao=representacao)
                    self.assertEqual(grafo.numero_vertices, 5)
                    self.assertEqual(grafo.numero_arestas, 5)
                    self.assertEqual(grafo.vizinhos(5), [1, 2, 3, 4])

    def test_ignora_linhas_vazias_e_comentarios(self) -> None:
        conteudo = "# grafo de teste\n\n3\n# arestas\n1 2\n\n2 3\n"
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever_temporario(conteudo, diretorio)
            grafo = Grafo.de_arquivo(caminho)
            self.assertEqual(grafo.numero_vertices, 3)
            self.assertEqual(grafo.numero_arestas, 2)

    def test_rejeita_arquivo_vazio(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever_temporario("\n # comentário\n", diretorio)
            with self.assertRaisesRegex(ValueError, "vazio"):
                Grafo.de_arquivo(caminho)

    def test_rejeita_numero_de_vertices_nao_inteiro(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever_temporario("cinco\n1 2\n", diretorio)
            with self.assertRaisesRegex(ValueError, "número de vértices inválido"):
                Grafo.de_arquivo(caminho)

    def test_rejeita_linha_de_aresta_com_quantidade_incorreta(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever_temporario("3\n1 2 3\n", diretorio)
            with self.assertRaisesRegex(ValueError, "exatamente dois vértices"):
                Grafo.de_arquivo(caminho)

    def test_rejeita_aresta_com_vertice_nao_inteiro(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever_temporario("3\n1 x\n", diretorio)
            with self.assertRaisesRegex(ValueError, "devem ser inteiros"):
                Grafo.de_arquivo(caminho)

    def test_rejeita_aresta_com_vertice_fora_do_grafo(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = self.escrever_temporario("3\n1 4\n", diretorio)
            with self.assertRaisesRegex(ValueError, "aresta inválida"):
                Grafo.de_arquivo(caminho)

    def test_rejeita_arquivo_inexistente(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "inexistente.txt"
            with self.assertRaises(OSError):
                Grafo.de_arquivo(caminho)


class TestArquivosDeSaida(unittest.TestCase):
    def criar_grafo(self, representacao: str = "lista") -> Grafo:
        grafo = Grafo(5, representacao=representacao)
        for u, v in ARESTAS_EXEMPLO:
            grafo.adicionar_aresta(u, v)
        return grafo

    def test_formata_estatisticas_do_exemplo(self) -> None:
        esperado = (
            "Estatísticas do grafo\n"
            "Número de vértices: 5\n"
            "Número de arestas: 5\n"
            "Grau mínimo: 1\n"
            "Grau máximo: 4\n"
            "Grau médio: 2.00\n"
        )
        self.assertEqual(formatar_estatisticas(self.criar_grafo()), esperado)

    def test_formata_pais_e_niveis_da_bfs(self) -> None:
        texto = formatar_resultado_bfs(self.criar_grafo(), origem=1)
        self.assertIn("Vértice;Pai;Nível\n", texto)
        self.assertIn("1;-;0\n", texto)
        self.assertIn("2;1;1\n", texto)
        self.assertIn("3;5;2\n", texto)
        self.assertIn("4;5;2\n", texto)
        self.assertIn("5;1;1\n", texto)

    def test_processa_entrada_e_cria_pastas_de_saida(self) -> None:
        conteudo = "5\n1 2\n2 5\n5 3\n4 5\n1 5\n"
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            entrada = self.escrever_entrada(raiz, conteudo)
            saida_estatisticas = raiz / "nova_pasta" / "estatisticas.txt"
            saida_bfs = raiz / "outra_pasta" / "bfs.txt"
            processar_arquivo(
                entrada,
                "matriz",
                1,
                saida_estatisticas,
                saida_bfs,
            )
            self.assertIn("Número de arestas: 5", saida_estatisticas.read_text(encoding="utf-8"))
            self.assertIn("4;5;2", saida_bfs.read_text(encoding="utf-8"))

    def escrever_entrada(self, raiz: Path, conteudo: str) -> Path:
        entrada = raiz / "entrada.txt"
        entrada.write_text(conteudo, encoding="utf-8")
        return entrada

    def test_vertices_inalcancaveis_aparecem_com_tracos(self) -> None:
        grafo = Grafo(4)
        grafo.adicionar_aresta(1, 2)
        texto = formatar_resultado_bfs(grafo, origem=1)
        self.assertIn("3;-;-\n", texto)
        self.assertIn("4;-;-\n", texto)

    def test_origem_invalida_nao_produz_resultado_bfs(self) -> None:
        with self.assertRaises(ValueError):
            formatar_resultado_bfs(self.criar_grafo(), origem=6)


if __name__ == "__main__":
    unittest.main()
