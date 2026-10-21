import logging
import os
from datetime import date, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.error import TelegramError
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from .config import (
    PREMIOS_TIMEZONE,
    get_horario_premios,
    get_telegram_chat_id,
    get_telegram_token,
)
from .leitor import ler_premios_do_dia


logger = logging.getLogger(__name__)


def _formatar_premios(hoje: date) -> str:
    lista_premios = ler_premios_do_dia(hoje=hoje)
    if not lista_premios:
        return "Não há prêmios registados para hoje."

    linhas = "\n".join(
        f"• {premio.data_hora:%H:%M} — {premio.categoria}"
        for premio in lista_premios
    )
    return f"prêmios de hoje:\n{linhas}"


async def start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message:
        await update.message.reply_text(
            "Olá! Use /premios para consultar os prêmios de hoje. "
            "Use /chatid para ver o ID deste chat."
        )


async def chatid(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message and update.effective_chat:
        await update.message.reply_text(
            f"ID deste chat: {update.effective_chat.id}"
        )


async def premios(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not update.message:
        return

    try:
        mensagem = _formatar_premios(
            datetime.now(PREMIOS_TIMEZONE).date()
        )
    except (OSError, ValueError):
        logger.exception("Não foi possível ler o arquivo de prêmios.")
        await update.message.reply_text(
            "Não foi possível consultar os prêmios. Verifique o arquivo "
            "data/premios.txt."
        )
        return

    await update.message.reply_text(mensagem)


async def enviar_premios_diarios(aplicacao: Application) -> None:
    try:
        chat_id = get_telegram_chat_id()
        mensagem = _formatar_premios(
            datetime.now(PREMIOS_TIMEZONE).date()
        )
        await aplicacao.bot.send_message(
            chat_id=chat_id,
            text=mensagem,
        )
    except (OSError, RuntimeError, ValueError):
        logger.exception("Não foi possível preparar a notificação diária.")
    except TelegramError:
        logger.exception("Não foi possível enviar a notificação diária.")


async def iniciar_agendador(aplicacao: Application) -> None:
    hora, minuto = get_horario_premios()
    agendador = AsyncIOScheduler(timezone=PREMIOS_TIMEZONE)
    agendador.add_job(
        enviar_premios_diarios,
        trigger="cron",
        hour=hora,
        minute=minuto,
        args=[aplicacao],
        id="notificacao-diaria-premios",
        replace_existing=True,
    )
    agendador.start()
    aplicacao.bot_data["agendador_premios"] = agendador
    logger.info(
        "Notificação diária agendada para %02d:%02d (%s).",
        hora,
        minuto,
        PREMIOS_TIMEZONE,
    )


async def parar_agendador(aplicacao: Application) -> None:
    agendador = aplicacao.bot_data.pop("agendador_premios", None)
    if agendador:
        agendador.shutdown(wait=False)


def executar_bot() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
    )
    if os.getenv("TELEGRAM_CHAT_ID"):
        get_telegram_chat_id()
    else:
        logger.warning(
            "TELEGRAM_CHAT_ID não configurado; use /chatid e defina-o no Portainer."
        )
    get_horario_premios()
    aplicacao = (
        Application.builder()
        .token(get_telegram_token())
        .post_init(iniciar_agendador)
        .post_shutdown(parar_agendador)
        .build()
    )
    aplicacao.add_handler(CommandHandler("start", start))
    aplicacao.add_handler(CommandHandler("chatid", chatid))
    aplicacao.add_handler(CommandHandler("premios", premios))
    aplicacao.run_polling()
