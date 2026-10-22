"""Testes das medições e da proteção de memória do script de experimentos."""

import csv
import tempfile
import unittest
from pathlib import Path

from experimentos import (
    avaliar_viabilidade_matriz,
    executar_experimentos,
    gerar_origens,
    medir_tempo_bfs,
)
from grafo import Grafo


class TestOrigensETempo(unittest.TestCase):
    def test_origens_distintas_e_reproduziveis(self) -> None:
        primeiras = gerar_origens(200, 100)
        segundas = gerar_origens(200, 100)
        self.assertEqual(primeiras, segundas)
        self.assertEqual(len(set(primeiras)), 100)

    def test_reutiliza_origens_somente_depois_de_usar_todas(self) -> None:
        origens = gerar_origens(3, 5)
        self.assertEqual(set(origens[:3]), {1, 2, 3})
        self.assertEqual(origens[3:], origens[:2])

    def test_rejeita_repeticoes_invalidas(self) -> None:
        with self.assertRaises(ValueError):
            gerar_origens(5, 0)

    def test_tempo_total_e_media_validos(self) -> None:
        grafo = Grafo(3)
        grafo.adicionar_aresta(1, 2)
        total, media = medir_tempo_bfs(grafo, [1, 2, 3])
        self.assertGreaterEqual(total, 0)
        self.assertGreaterEqual(media, 0)
        self.assertAlmostEqual(media, total / 3, places=8)

    def test_matriz_grande_e_recusada_sem_tentar_alocar(self) -> None:
        viavel, estimativa, motivo = avaliar_viabilidade_matriz(
            4_843_750, memoria_disponivel_bytes=16_000_000_000
        )
        self.assertFalse(viavel)
        self.assertGreater(estimativa, 16_000_000_000)
        self.assertIn("Matriz estimada", motivo)


class TestExecucaoExperimentos(unittest.TestCase):
    def test_execucao_gera_csv_das_duas_representacoes(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            entrada = raiz / "grafo.txt"
            saida = raiz / "resultados" / "experimentos.csv"
            entrada.write_text("5\n1 2\n2 5\n5 3\n4 5\n1 5\n", encoding="utf-8")
            resultados = executar_experimentos(entrada, repeticoes=10, caminho_saida=saida)
            self.assertEqual([r["representacao"] for r in resultados], ["lista", "matriz"])
            self.assertTrue(all(r["status"] == "ok" for r in resultados))
            self.assertTrue(all(r["numero_vertices"] == 5 for r in resultados))
            self.assertEqual(resultados[0]["origens_distintas"], 5)
            with saida.open(newline="", encoding="utf-8") as arquivo:
                linhas = list(csv.DictReader(arquivo))
            self.assertEqual(len(linhas), 2)
            self.assertEqual(linhas[0]["representacao"], "lista")

    def test_estimativa_e_segura_com_orcamento_baixo(self) -> None:
        viavel, estimativa, motivo = avaliar_viabilidade_matriz(
            10_000, memoria_disponivel_bytes=100_000_000
        )
        self.assertFalse(viavel)
        self.assertGreater(estimativa, 100_000_000)
        self.assertIn("memória disponível", motivo)
