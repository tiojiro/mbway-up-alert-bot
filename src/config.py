import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


PREMIOS_TIMEZONE_NAME = os.getenv("PREMIOS_TIMEZONE", "Europe/Lisbon")
try:
    PREMIOS_TIMEZONE = ZoneInfo(PREMIOS_TIMEZONE_NAME)
except ZoneInfoNotFoundError as erro:
    raise RuntimeError(
        f"Fuso horário inválido em PREMIOS_TIMEZONE: {PREMIOS_TIMEZONE_NAME}."
    ) from erro


def get_telegram_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Defina a variável de ambiente TELEGRAM_BOT_TOKEN com o token do bot."
        )
    return token


def get_telegram_chat_id() -> int:
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        raise RuntimeError(
            "Defina a variável de ambiente TELEGRAM_CHAT_ID com o chat de destino."
        )

    try:
        valor = int(chat_id)
    except ValueError as erro:
        raise RuntimeError("TELEGRAM_CHAT_ID deve ser um número inteiro.") from erro
    if valor == 0:
        raise RuntimeError("TELEGRAM_CHAT_ID não pode ser zero.")
    return valor


def get_horario_premios() -> tuple[int, int]:
    horario = os.getenv("PREMIOS_HORARIO", "06:00")
    if not re.fullmatch(r"\d{2}:\d{2}", horario):
        raise RuntimeError("PREMIOS_HORARIO deve estar no formato HH:MM.")

    try:
        horario_validado = datetime.strptime(horario, "%H:%M").time()
    except ValueError as erro:
        raise RuntimeError(
            "PREMIOS_HORARIO deve conter uma hora válida no formato HH:MM."
        ) from erro
    return horario_validado.hour, horario_validado.minute
