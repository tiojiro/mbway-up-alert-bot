FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PREMIOS_FILE=/app/data/premios.txt \
    PREMIOS_HORARIO=06:00 \
    PREMIOS_TIMEZONE=Europe/Lisbon

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 botuser

COPY --chown=botuser:botuser src ./src
COPY --chown=botuser:botuser data ./data
COPY --chown=botuser:botuser main.py .

USER botuser

CMD ["python", "main.py"]
