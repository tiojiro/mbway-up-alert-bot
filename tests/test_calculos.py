import unittest
from datetime import date, datetime

from src.calculos import Premio, obter_premios_do_dia


class ObterPremiosDoDiaTests(unittest.TestCase):
    def test_premios_na_data_de_inicio(self) -> None:
        premios = obter_premios_do_dia(date(2021, 9, 25))

        self.assertEqual(
            premios,
            [
                Premio(datetime(2021, 9, 25, 10, 24), "Diário"),
                Premio(datetime(2021, 9, 25, 13, 0), "Mensal"),
                Premio(datetime(2021, 9, 25, 21, 45), "Semanal"),
            ],
        )

    def test_premio_diario_avanca_hora_e_minutos(self) -> None:
        premios = obter_premios_do_dia(date(2021, 9, 23))

        self.assertEqual(
            [(premio.categoria, premio.data_hora) for premio in premios],
            [("Diário", datetime(2021, 9, 23, 8, 36))],
        )

    def test_premio_diario_reinicia_hora_apos_23(self) -> None:
        premios = obter_premios_do_dia(date(2021, 10, 9))

        self.assertEqual(
            [(premio.categoria, premio.data_hora) for premio in premios],
            [("Diário", datetime(2021, 10, 9, 7, 0))],
        )

    def test_premio_semanal_avanca_dia_e_alterna_minutos(self) -> None:
        premios = obter_premios_do_dia(date(2021, 10, 20))

        self.assertEqual(
            [(premio.categoria, premio.data_hora) for premio in premios],
            [
                ("Semanal", datetime(2021, 10, 20, 15, 45)),
                ("Diário", datetime(2021, 10, 20, 18, 24)),
            ],
        )

    def test_premio_semanal_segue_sequencia_dos_dias(self) -> None:
        eventos = (
            (date(2021, 10, 3), datetime(2021, 10, 3, 9, 15)),
            (date(2021, 10, 4), datetime(2021, 10, 4, 11, 45)),
            (date(2021, 10, 12), datetime(2021, 10, 12, 13, 15)),
            (date(2021, 10, 20), datetime(2021, 10, 20, 15, 45)),
            (date(2021, 10, 28), datetime(2021, 10, 28, 17, 15)),
            (date(2021, 11, 5), datetime(2021, 11, 5, 19, 45)),
            (date(2021, 11, 13), datetime(2021, 11, 13, 21, 15)),
            (date(2021, 11, 21), datetime(2021, 11, 21, 9, 45)),
            (date(2021, 11, 22), datetime(2021, 11, 22, 11, 15)),
        )

        for dia, data_hora_esperada in eventos:
            with self.subTest(dia=dia):
                premio_semanal = next(
                    premio
                    for premio in obter_premios_do_dia(dia)
                    if premio.categoria == "Semanal"
                )
                self.assertEqual(premio_semanal.data_hora, data_hora_esperada)

    def test_premios_semanais_de_dezembro_de_2026(self) -> None:
        eventos = (
            (date(2026, 12, 3), datetime(2026, 12, 3, 17, 15)),
            (date(2026, 12, 11), datetime(2026, 12, 11, 19, 45)),
            (date(2026, 12, 19), datetime(2026, 12, 19, 21, 15)),
            (date(2026, 12, 27), datetime(2026, 12, 27, 9, 45)),
            (date(2026, 12, 28), datetime(2026, 12, 28, 11, 15)),
        )

        for dia, data_hora_esperada in eventos:
            with self.subTest(dia=dia):
                premio_semanal = next(
                    premio
                    for premio in obter_premios_do_dia(dia)
                    if premio.categoria == "Semanal"
                )
                self.assertEqual(premio_semanal.data_hora, data_hora_esperada)

    def test_diario_e_mensal_em_dezembro_de_2026(self) -> None:
        premio_diario = next(
            premio
            for premio in obter_premios_do_dia(date(2026, 12, 3))
            if premio.categoria == "Diário"
        )
        premio_mensal = next(
            premio
            for premio in obter_premios_do_dia(date(2026, 12, 26))
            if premio.categoria == "Mensal"
        )

        self.assertEqual(premio_diario.data_hora, datetime(2026, 12, 3, 18, 24))
        self.assertEqual(premio_mensal.data_hora, datetime(2026, 12, 26, 8, 0))

    def test_premio_mensal_ocorre_no_ultimo_sabado_e_reinicia_hora(self) -> None:
        premios = obter_premios_do_dia(date(2022, 8, 27))

        self.assertEqual(
            [(premio.categoria, premio.data_hora) for premio in premios],
            [
                ("Mensal", datetime(2022, 8, 27, 7, 0)),
                ("Diário", datetime(2022, 8, 27, 23, 48)),
            ],
        )

    def test_data_anterior_ao_inicio_nao_tem_premios(self) -> None:
        self.assertEqual(obter_premios_do_dia(date(2021, 9, 21)), [])


if __name__ == "__main__":
    unittest.main()
