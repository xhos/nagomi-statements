from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

import fitz


class UnrecognizedStatement(Exception):
  pass


@dataclass
class Line:
  date: date
  # signed: negative is money leaving the account
  amount_cents: int
  description: str
  posting_date: date | None = None


@dataclass
class Statement:
  parser: str
  bank: str
  # chequing | savings | credit_card
  account_type: str
  account_number: str
  period_start: date
  period_end: date
  currency: str = "CAD"
  opening_balance_cents: int | None = None
  closing_balance_cents: int | None = None
  lines: list[Line] = field(default_factory=list)


def parse_cents(string: str) -> int:
  cleaned = string.replace("$", "").replace(",", "").strip()
  return int((Decimal(cleaned) * 100).to_integral_value())


class Pdf:
  def __init__(self, data: bytes):
    try:
      self._doc = fitz.open(stream=data, filetype="pdf")
    except Exception as e:
      raise UnrecognizedStatement(f"not a readable pdf: {e}") from e
    self._text: str | None = None
    self._html: str | None = None

  def text(self) -> str:
    if self._text is None:
      self._text = "".join(page.get_text("text") for page in self._doc)
    return self._text

  def html(self) -> str:
    if self._html is None:
      self._html = "".join(page.get_text("html") for page in self._doc)
    return self._html
