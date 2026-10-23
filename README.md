# MB WAY UP Alert Bot

Bot de Telegram que consulta os horários dos prêmios do MB WAY UP e envia notificações para um chat configurado.

## Funcionalidades

- `/start`: apresenta uma mensagem de boas-vindas.
- `/premios`: mostra os prêmios previstos para o dia.
- Envia uma notificação diária no horário configurado.
- Envia lembretes dois minutos antes de cada prêmio do dia.

Os horários usam o fuso `Europe/Lisbon` por padrão.

## Requisitos

- Python 3.12 ou superior.
- Um bot do Telegram e o respetivo token.
- O ID do chat que receberá as notificações.

## Configuração

Defina as seguintes variáveis de ambiente:

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Sim | — | Token do bot fornecido pelo Telegram. |
| `TELEGRAM_CHAT_ID` | Sim | — | ID numérico do chat de destino. |
| `PREMIOS_HORARIO` | Não | `06:00` | Horário de envio da mensagem diária, no formato `HH:MM`. |
| `PREMIOS_TIMEZONE` | Não | `Europe/Lisbon` | Fuso horário usado para as notificações. |

Não publique o token do bot em repositórios ou logs.

## Executar localmente

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Defina `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` no ambiente e inicie o bot:

```bash
python main.py
```

## Executar com Docker Compose

O projeto inclui `Dockerfile` e `compose.yaml`. Defina `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` no ambiente antes de iniciar o serviço.

```bash
docker compose up -d --build
```

## Regras dos prêmios

Os horários são calculados em `src/calculos.py`, sem arquivo de dados externo:

- **Diário:** começa em 22/09/2021 às 07:12. A cada dia, a hora avança uma unidade (reiniciando em 07 após 23) e os minutos avançam 24 (reiniciando após 59).
- **Semanal:** começa em 25/09/2021 às 21:45. A próxima data avança oito dias, exceto quando o prêmio anterior cai num domingo, quando avança um dia. A hora depende do dia da semana e os minutos alternam entre 15 e 45, começando em 15 no primeiro prêmio calculado após a data inicial.
- **Mensal:** ocorre no último sábado do mês, a partir de 25/09/2021 às 13:00. A cada mês, a hora avança uma unidade (reiniciando em 07 após 23).
