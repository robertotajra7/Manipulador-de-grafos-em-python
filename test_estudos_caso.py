"""Testes para as consultas específicas dos estudos de caso."""

import csv
import tempfile
import unittest
from pathlib import Path

from estudos_caso import CAMPOS_CSV, gravar_csv, processar_grafo


class TestEstudosCaso(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        self.entrada = self.root / "cadeia.txt"
        # Grafo-cadeia com vértices 1..30: existe aresta i -- i+1.
        linhas = ["30"] + [f"{u} {u + 1}" for u in range(1, 30)]
        self.entrada.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    def test_pais_e_distancias_em_uma_cadeia(self) -> None:
        resultado = processar_grafo(self.entrada)
        self.assertEqual(resultado["numero_vertices"], 30)
        self.assertEqual(resultado["numero_arestas"], 29)

        for origem in (1, 2, 3):
            with self.subTest(origem=origem):
                self.assertEqual(resultado[f"pai_10_bfs_origem_{origem}"], 9)
                self.assertEqual(resultado[f"pai_20_bfs_origem_{origem}"], 19)
                self.assertEqual(resultado[f"pai_30_bfs_origem_{origem}"], 29)

        self.assertEqual(resultado["distancia_10_20"], 10)
        self.assertEqual(resultado["distancia_10_30"], 20)
        self.assertEqual(resultado["distancia_20_30"], 10)

    def test_vertice_inalcancavel_e_identificado(self) -> None:
        # Componentes {1,2} e {10,20}; vértice 30 permanece isolado.
        self.entrada.write_text("30\n1 2\n10 20\n", encoding="utf-8")
        resultado = processar_grafo(self.entrada)
        self.assertEqual(resultado["pai_10_bfs_origem_1"], "inalcancavel")
        self.assertEqual(resultado["distancia_10_20"], 1)
        self.assertEqual(resultado["distancia_10_30"], "inalcancavel")
        self.assertEqual(resultado["distancia_20_30"], "inalcancavel")

    def test_rejeita_grafo_com_menos_de_trinta_vertices(self) -> None:
        self.entrada.write_text("20\n1 2\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "pelo menos 30"):
            processar_grafo(self.entrada)

    def test_grava_csv_com_cabecalho_e_resultado(self) -> None:
        resultado = processar_grafo(self.entrada)
        destino = self.root / "subpasta" / "resultado.csv"
        gravar_csv(resultado, destino)
        with destino.open(newline="", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)
            linhas = list(leitor)
        self.assertEqual(leitor.fieldnames, CAMPOS_CSV)
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["distancia_10_30"], "20")


if __name__ == "__main__":
    unittest.main(verbosity=2)
