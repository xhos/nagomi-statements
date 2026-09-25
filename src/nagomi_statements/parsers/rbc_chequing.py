# RBC chequing and savings statements. layout rules ported from
# andrewscwei/rbc-statement-parser (MIT, see LICENSE.rbc-statement-parser):
# columns are told apart by each text run's left offset in mupdf's html output.
import re
from datetime import date, datetime

from bs4 import BeautifulSoup

from .common import Line, Pdf, Statement, UnrecognizedStatement, parse_cents

PAT_MONTH_SHORT = r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
PAT_MONTH_LONG = r"january|february|march|april|may|june|july|august|september|october|november|december"
PAT_DAY = r"\d{1,2}"
PAT_YEAR = r"\d{4}"
PAT_DATE_SHORT = rf"{PAT_DAY} (?:{PAT_MONTH_SHORT})"
PAT_DATE_LONG = rf"((?:{PAT_MONTH_LONG})) ({PAT_DAY})(?:, )?({PAT_YEAR})?"
PAT_AMOUNT = r"-?\$?[\d,]+\.\d{2}"
PAT_PARAGRAPH = r"^<p.*</p>$"

SAVINGS_MARKER = "personal savings account statement"
CHEQUING_MARKER = "personal banking account statement"


def detect(text: str) -> str | None:
  header = text[:3000].lower()
  if SAVINGS_MARKER in header:
    return "savings"
  if CHEQUING_MARKER in header:
    return "chequing"
  return None


def extract_period(pdf: str) -> tuple[date, date]:
  regex = rf"from ({PAT_DATE_LONG}) to ({PAT_DATE_LONG})"
  match = re.search(regex, pdf, re.IGNORECASE)
  if not match:
    raise UnrecognizedStatement("could not find the statement period")

  end_year = match[8]
  start = datetime.strptime(f"{match[2]} {match[3]} {match[4] or end_year}", "%B %d %Y")
  end = datetime.strptime(f"{match[6]} {match[7]} {end_year}", "%B %d %Y")
  return start.date(), end.date()


def extract_account_number(text: str) -> str:
  if match := re.search(r"account number[:\s]+([0-9-]+)", text, re.IGNORECASE):
    return match.group(1)
  return ""


def _left_padding(soup: BeautifulSoup) -> float:
  style = soup.p.attrs.get("style", "")
  match = re.search(r"left:([0-9.]+)pt", style, re.IGNORECASE)
  return float(match.group(1)) if match else 0


def _date(soup: BeautifulSoup, start: date) -> date | None:
  padding = _left_padding(soup)
  if not (10 < padding < 20 or 40 < padding < 50):
    return None
  if not re.match(rf"^{PAT_DATE_SHORT}$", soup.text, re.IGNORECASE):
    return None

  # statements can span new year; a month before the start month is next year
  ref = datetime.strptime(f"{soup.text} {start.year}", "%d %b %Y")
  year = start.year + (1 if ref.month < start.month else 0)
  return datetime.strptime(f"{soup.text} {year}", "%d %b %Y").date()


def _description(soup: BeautifulSoup) -> str | None:
  padding = _left_padding(soup)
  if 60 < padding < 75 or 85 < padding < 100:
    return soup.text
  return None


def _amount_in(soup: BeautifulSoup, low: float, high: float) -> int | None:
  padding = _left_padding(soup)
  if low < padding < high and re.match(rf"^{PAT_AMOUNT}$", soup.text, re.IGNORECASE):
    return parse_cents(soup.text)
  return None


def parse_lines(html: str, start: date) -> list[Line]:
  lines: list[Line] = []
  tx_date: date | None = None
  description: str | None = None

  for raw in html.splitlines():
    if not re.match(PAT_PARAGRAPH, raw, re.IGNORECASE):
      continue
    soup = BeautifulSoup(raw, "html.parser")
    amount: int | None = None

    if d := _date(soup, start):
      tx_date = d
    elif tx_date and (text := _description(soup)):
      description = f"{description} {text}" if description else text
    elif description and (withdrawal := _amount_in(soup, 250, 360)):
      amount = -withdrawal
    elif description and (deposit := _amount_in(soup, 360, 460)):
      amount = deposit

    if tx_date and description and amount:
      lines.append(Line(date=tx_date, posting_date=tx_date, amount_cents=amount, description=description))
      # the date column is only printed on a day's first transaction
      description = None

  return lines


def parse(pdf: Pdf, kind: str) -> Statement:
  html = pdf.html()
  start, end = extract_period(html)

  return Statement(
    parser=f"rbc-{kind}",
    bank="RBC",
    account_type=kind,
    account_number=extract_account_number(pdf.text()),
    period_start=start,
    period_end=end,
    lines=parse_lines(html, start),
  )
