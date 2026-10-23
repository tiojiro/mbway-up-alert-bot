import logging
from datetime import date, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
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
    return f"🏆 Prêmio(s) de hoje:\n{linhas}"


async def start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message:
        await update.message.reply_text(
            "Olá! Use /premios para consultar os prêmios de hoje."
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

    _agendar_lembretes_premios(aplicacao)


async def enviar_lembrete_premio(
    aplicacao: Application, categoria: str
) -> None:
    try:
        await aplicacao.bot.send_message(
            chat_id=get_telegram_chat_id(),
            text=f"🔔Lembrete: Prêmio {categoria} em 2 minutos!",
        )
    except (RuntimeError, TelegramError):
        logger.exception("Não foi possível enviar o lembrete do prêmio %s.", categoria)


def _agendar_lembretes_premios(
    aplicacao: Application, agora: datetime | None = None
) -> int:
    agendador = aplicacao.bot_data.get("agendador_premios")
    if agendador is None:
        logger.error("Agendador de prêmios indisponível; lembretes não agendados.")
        return 0

    instante_atual = agora or datetime.now(PREMIOS_TIMEZONE)
    try:
        premios = ler_premios_do_dia(hoje=instante_atual.date())
    except (OSError, ValueError):
        logger.exception("Não foi possível carregar os prêmios para agendar lembretes.")
        return 0

    quantidade_agendada = 0
    for premio in premios:
        horario_premio = premio.data_hora.replace(tzinfo=PREMIOS_TIMEZONE)
        horario_lembrete = horario_premio - timedelta(minutes=2)
        if horario_lembrete <= instante_atual:
            continue

        identificador = (
            f"lembrete-{premio.data_hora:%Y%m%d-%H%M}-{premio.categoria.casefold()}"
        )
        agendador.add_job(
            enviar_lembrete_premio,
            trigger=DateTrigger(
                run_date=horario_lembrete,
                timezone=PREMIOS_TIMEZONE,
            ),
            args=[aplicacao, premio.categoria],
            id=identificador,
            replace_existing=True,
        )
        quantidade_agendada += 1

    logger.info(
        "%d lembrete(s) de prêmios agendado(s) para hoje.",
        quantidade_agendada,
    )
    return quantidade_agendada


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
    aplicacao.bot_data["agendador_premios"] = agendador
    agendador.start()
    _agendar_lembretes_premios(aplicacao)
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
    logging.getLogger("httpx").setLevel(logging.WARNING)
    get_telegram_chat_id()
    get_horario_premios()
    aplicacao = (
        Application.builder()
        .token(get_telegram_token())
        .post_init(iniciar_agendador)
        .post_shutdown(parar_agendador)
        .build()
    )
    aplicacao.add_handler(CommandHandler("start", start))
    aplicacao.add_handler(CommandHandler("premios", premios))
    aplicacao.run_polling()
