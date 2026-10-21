from dataclasses import dataclass
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
import re
from typing import List, Optional

from .config import PREMIOS_FILE


@dataclass
class Premio:
    data_hora: datetime
    categoria: str


class _TabelaPremiosParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.linhas: List[List[str]] = []
        self._linha_atual: List[str] = []
        self._celula_atual: Optional[List[str]] = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "tr":
            self._linha_atual = []
        elif tag == "td":
            self._celula_atual = []
        elif tag == "br" and self._celula_atual is not None:
            self._celula_atual.append("\n")

    def handle_data(self, data: str) -> None:
        if self._celula_atual is not None:
            self._celula_atual.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._celula_atual is not None:
            self._linha_atual.append("".join(self._celula_atual).strip())
            self._celula_atual = None
        elif tag == "tr" and self._linha_atual:
            self.linhas.append(self._linha_atual)
            self._linha_atual = []


def ler_premios_do_dia(
    caminho: Optional[Path] = None, hoje: Optional[date] = None
) -> List[Premio]:
    arquivo = caminho or PREMIOS_FILE
    data_atual = hoje or date.today()
    premios = []

    parser = _TabelaPremiosParser()
    with arquivo.open(encoding="utf-8") as ficheiro:
        parser.feed(ficheiro.read())
    parser.close()

    if len(parser.linhas) < 2:
        raise ValueError(f"Nenhuma tabela de prémios válida encontrada em {arquivo}.")

    categorias = [celula.casefold() for celula in parser.linhas[0]]
    if not all(categoria in categorias for categoria in ("diário", "semanal", "mensal")):
        raise ValueError(
            f"A tabela em {arquivo} deve conter as colunas Diário, Semanal e Mensal."
        )

    padrao_data = re.compile(r"\d{2}/\d{2}/\d{4}\s*-\s*\d{2}:\d{2}")
    for numero_linha, linha in enumerate(parser.linhas[1:], start=2):
        if len(linha) != len(categorias):
            raise ValueError(
                f"Número de colunas inválido na linha {numero_linha} da tabela "
                f"em {arquivo}."
            )

        for categoria, conteudo in zip(categorias, linha):
            if categoria not in ("diário", "semanal", "mensal"):
                continue

            for valor in conteudo.splitlines():
                valor = valor.strip()
                if not valor:
                    continue
                if not padrao_data.fullmatch(valor):
                    raise ValueError(
                        f"Data ou hora inválida na linha {numero_linha} da tabela "
                        f"em {arquivo}: {valor!r}."
                    )

                data_hora = datetime.strptime(valor, "%d/%m/%Y - %H:%M")
                if data_hora.date() == data_atual:
                    premios.append(Premio(data_hora, categoria.capitalize()))

    return sorted(premios, key=lambda premio: premio.data_hora)
