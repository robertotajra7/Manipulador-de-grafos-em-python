"""Testes das rotinas de experimento de desempenho."""

import csv
import tempfile
import unittest
from pathlib import Path

from experimentos import (
    executar_experimentos,
    gerar_origens,
    medir_tempo_bfs,
)
from grafo import Grafo


class TestOrigensETemporizacao(unittest.TestCase):
    def test_usa_origens_diferentes_quando_ha_vertices_suficientes(self) -> None:
        self.assertEqual(gerar_origens(120, 100), list(range(1, 101)))

    def test_reutiliza_origens_somente_apos_visitar_todos_os_vertices(self) -> None:
        self.assertEqual(gerar_origens(3, 5), [1, 2, 3, 1, 2])

    def test_rejeita_quantidade_de_repeticoes_invalida(self) -> None:
        with self.assertRaises(ValueError):
            gerar_origens(5, 0)

    def test_tempo_total_e_media_sao_nao_negativos(self) -> None:
        grafo = Grafo(3, representacao="lista")
        grafo.adicionar_aresta(1, 2)
        origens = [1, 2, 3]
        total_ms, media_ms = medir_tempo_bfs(grafo, origens)
        self.assertGreaterEqual(total_ms, 0)
        self.assertGreaterEqual(media_ms, 0)
        self.assertAlmostEqual(media_ms, total_ms / len(origens), places=9)


class TestExecucaoExperimentos(unittest.TestCase):
    def setUp(self) -> None:
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.diretorio_temporario.cleanup)
        raiz = Path(self.diretorio_temporario.name)
        self.entrada = raiz / "grafo.txt"
        self.saida = raiz / "resultados" / "experimentos.csv"
        self.entrada.write_text(
            "5\n1 2\n2 5\n5 3\n4 5\n1 5\n", encoding="utf-8"
        )

    def test_executa_as_duas_representacoes_e_cria_csv(self) -> None:
        resultados = executar_experimentos(
            self.entrada, repeticoes=10, caminho_saida=self.saida
        )

        self.assertEqual(
            [linha["representacao"] for linha in resultados], ["lista", "matriz"]
        )
        for linha in resultados:
            with self.subTest(representacao=linha["representacao"]):
                self.assertEqual(linha["numero_vertices"], 5)
                self.assertEqual(linha["numero_arestas"], 5)
                self.assertEqual(linha["repeticoes"], 10)
                self.assertEqual(linha["origens_distintas"], 5)
                self.assertGreater(linha["memoria_residente_mb"], 0)
                self.assertGreaterEqual(linha["tempo_medio_ms"], 0)

        self.assertTrue(self.saida.is_file())
        with self.saida.open(newline="", encoding="utf-8") as arquivo_csv:
            linhas_csv = list(csv.DictReader(arquivo_csv))
        self.assertEqual(len(linhas_csv), 2)
        self.assertEqual(linhas_csv[0]["representacao"], "lista")
        self.assertEqual(linhas_csv[1]["representacao"], "matriz")


if __name__ == "__main__":
    unittest.main()
