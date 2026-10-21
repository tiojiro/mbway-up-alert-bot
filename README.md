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
| `PREMIOS_HORARIO` | Não | `06:00` | Horário da notificação diária, no formato `HH:MM`. |
| `PREMIOS_TIMEZONE` | Não | `Europe/Lisbon` | Fuso horário usado para as notificações. |
| `PREMIOS_FILE` | Não | `data/premios.txt` | Caminho do arquivo com os horários dos prêmios. |

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

O projeto inclui `Dockerfile` e `compose.yaml`. O Compose requer `TELEGRAM_BOT_TOKEN` no ambiente. O `TELEGRAM_CHAT_ID` está definido diretamente no `compose.yaml`; ajuste-o para o chat pretendido antes de iniciar o serviço.

O arquivo Compose monta `/data/mbway_up_premios` como `/data` dentro do contêiner. Esse diretório deve conter `premios.txt`.

```bash
docker compose up -d --build
```

## Formato do arquivo de prêmios

O arquivo deve conter uma tabela HTML com as colunas `Diário`, `Semanal` e `Mensal`. Cada horário deve seguir o formato `DD/MM/AAAA - HH:MM`; várias datas podem ser separadas por quebras de linha ou tags `<br>` dentro da respetiva célula.

Exemplo:

```html
<table>
  <tr>
    <td>Diário</td>
    <td>Semanal</td>
    <td>Mensal</td>
  </tr>
  <tr>
    <td>21/10/2026 - 12:30<br>22/10/2026 - 13:00</td>
    <td>25/10/2026 - 18:00</td>
    <td>01/11/2026 - 20:00</td>
  </tr>
</table>
```
