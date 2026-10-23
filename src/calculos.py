from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass(frozen=True)
class Premio:
    data_hora: datetime
    categoria: str


_INICIO_DIARIO = datetime(2021, 9, 22, 7, 12)
_INICIO_SEMANAL = datetime(2021, 9, 25, 21, 45)
_INICIO_MENSAL = datetime(2021, 9, 25, 13, 0)
_HORAS_SEMANAIS = {
    0: 11,
    1: 13,
    2: 15,
    3: 17,
    4: 19,
    5: 21,
    6: 9,
}


def _premio_diario(dia: date) -> Premio | None:
    dias_desde_inicio = (dia - _INICIO_DIARIO.date()).days
    if dias_desde_inicio < 0:
        return None

    hora = 7 + dias_desde_inicio % 17
    minuto = (12 + 24 * dias_desde_inicio) % 60
    return Premio(datetime.combine(dia, time(hora, minuto)), "Diário")


def _premio_semanal(dia: date) -> Premio | None:
    if dia == _INICIO_SEMANAL.date():
        return Premio(_INICIO_SEMANAL, "Semanal")
    if dia < _INICIO_SEMANAL.date():
        return None

    data_premio = _INICIO_SEMANAL.date()
    indice_premio = 0

    while True:
        intervalo = 1 if data_premio.weekday() == 6 else 8
        proxima_data = data_premio + timedelta(days=intervalo)
        if proxima_data > dia:
            return None

        dia_semana = proxima_data.weekday()
        minuto = 15 if indice_premio % 2 == 0 else 45
        data_premio = proxima_data
        if data_premio == dia:
            horario = time(_HORAS_SEMANAIS[dia_semana], minuto)
            return Premio(datetime.combine(data_premio, horario), "Semanal")
        indice_premio += 1


def _ultimo_sabado(ano: int, mes: int) -> date:
    ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
    return ultimo_dia - timedelta(days=(ultimo_dia.weekday() - 5) % 7)


def _premio_mensal(dia: date) -> Premio | None:
    if dia < _INICIO_MENSAL.date():
        return None

    data_premio = _ultimo_sabado(dia.year, dia.month)
    if dia != data_premio:
        return None

    meses_desde_inicio = (dia.year - _INICIO_MENSAL.year) * 12
    meses_desde_inicio += dia.month - _INICIO_MENSAL.month
    hora = 7 + (6 + meses_desde_inicio) % 17
    return Premio(datetime.combine(dia, time(hora, 0)), "Mensal")


def obter_premios_do_dia(dia: date) -> list[Premio]:
    premios = [
        premio
        for premio in (
            _premio_diario(dia),
            _premio_semanal(dia),
            _premio_mensal(dia),
        )
        if premio is not None
    ]
    return sorted(premios, key=lambda premio: premio.data_hora)
