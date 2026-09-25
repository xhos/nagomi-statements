# RBC visa statements. line rules ported from andrewscwei/rbc-statement-parser
# (MIT, see LICENSE.rbc-statement-parser).
import re
from datetime import date, datetime

from .common import Line, Pdf, Statement, UnrecognizedStatement, parse_cents

PAT_MONTH = r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
PAT_DAY = r"\d{1,2}"
PAT_YEAR = r"\d{4}"
PAT_DATE_SHORT = rf"(?:{PAT_MONTH}) {PAT_DAY}"
PAT_DATE_LONG = rf"((?:{PAT_MONTH})) ({PAT_DAY})(?:, )?({PAT_YEAR})?"
PAT_AMOUNT = r"-?\$[\d,]+\.\d{2}"
PAT_CODE = r"\d{23}"
PAT_PERIOD = rf"statement from ({PAT_DATE_LONG}) to ({PAT_DATE_LONG})"


def _parse_date(string: str) -> date:
  return datetime.strptime(string, "%b %d %Y").date()


def detect(text: str) -> bool:
  header = text[:5000].replace("\xa0", " ").lower()
  return "visa" in header and re.search(PAT_PERIOD, header) is not None


def extract_period(text: str) -> tuple[date, date]:
  match = re.search(PAT_PERIOD, text.replace("\xa0", " "), re.IGNORECASE)
  if not match:
    raise UnrecognizedStatement("could not find the statement period")

  end_year = match[8]
  start = _parse_date(f"{match[2]} {match[3]} {match[4] or end_year}")
  end = _parse_date(f"{match[6]} {match[7]} {end_year}")
  return start, end


def extract_account_number(text: str) -> str:
  # card numbers are printed masked, e.g. "4516 12** **** 1234"; keep the last 4
  if match := re.search(r"(\d{4})\s+\d{2}\*\*\s+\*\*\*\*\s+(\d{4})", text):
    return match.group(2)
  return ""


def _dated(short: str, start: date) -> date:
  # statements can span new year; a month before the start month is next year
  ref = _parse_date(f"{short} {start.year}")
  year = start.year + (1 if ref.month < start.month else 0)
  return _parse_date(f"{short} {year}")


def parse_line(line: str, start: date) -> Line | None:
  match = re.match(
    rf"^({PAT_DATE_SHORT})\s+?({PAT_DATE_SHORT})\s+?(.*?)\s+?({PAT_AMOUNT})",
    line,
    re.IGNORECASE,
  )
  if match is None:
    return None

  tx_date, posting_date, body, amount = match.groups()
  code = res.group(0) if (res := re.search(PAT_CODE, body)) else None
  description = body.replace(f" {code}", "") if code else body

  return Line(
    date=_dated(tx_date, start),
    posting_date=_dated(posting_date, start),
    # charges are printed positive, payments negative
    amount_cents=-parse_cents(amount),
    description=description.strip(),
  )


def parse_lines(text: str, start: date) -> list[Line]:
  # a transaction's fields are split over several text lines; join everything
  # that isn't the start of a new "<date>\n<date>" pair
  joined = re.sub(
    rf"\n(?!{PAT_DATE_SHORT}\n{PAT_DATE_SHORT})",
    " ",
    text,
    flags=re.IGNORECASE,
  )
  return [line for raw in joined.splitlines() if (line := parse_line(raw, start))]


def parse(pdf: Pdf) -> Statement:
  text = pdf.text()
  start, end = extract_period(text)

  return Statement(
    parser="rbc-visa",
    bank="RBC",
    account_type="credit_card",
    account_number=extract_account_number(text),
    period_start=start,
    period_end=end,
    lines=parse_lines(text, start),
  )
