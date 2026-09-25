from datetime import date

import fitz
import pytest

from nagomi_statements import parsers
from nagomi_statements.parsers import rbc_visa
from nagomi_statements.parsers.common import parse_cents


def make_pdf(rows: list[tuple[float, float, str]]) -> bytes:
  """rows of (x, y, text) in points, drawn onto one letter page"""
  doc = fitz.open()
  page = doc.new_page(width=612, height=792)
  for x, y, text in rows:
    page.insert_text((x, y), text, fontsize=8)
  return doc.tobytes()


# column x offsets the chequing parser keys on
DATE_X, DESC_X, WITHDRAWAL_X, DEPOSIT_X, BALANCE_X = 15, 70, 300, 400, 500


def chequing_pdf(kind_marker: str, period: str, rows: list[tuple]) -> bytes:
  content = [
    (40, 40, kind_marker),
    (40, 55, period),
    (40, 70, "Account number: 05172-5163878"),
  ]
  y = 120
  for tx_date, description, withdrawal, deposit in rows:
    if tx_date:
      content.append((DATE_X, y, tx_date))
    content.append((DESC_X, y, description))
    if withdrawal:
      content.append((WITHDRAWAL_X, y, withdrawal))
    if deposit:
      content.append((DEPOSIT_X, y, deposit))
    content.append((BALANCE_X, y, "1,000.00"))
    y += 14
  return make_pdf(content)


def test_parse_cents():
  assert parse_cents("$1,234.56") == 123456
  assert parse_cents("-$0.10") == -10
  assert parse_cents("4.35") == 435


def test_chequing():
  pdf = chequing_pdf(
    "Your RBC personal banking account statement",
    "From December 15, 2025 to January 14, 2026",
    [
      ("16 Dec", "Payroll Deposit ACME", None, "2,500.00"),
      (None, "Interac purchase - COFFEE", "4.35", None),
      ("3 Jan", "e-Transfer sent", "120.00", None),
    ],
  )

  s = parsers.parse(pdf)

  assert s.parser == "rbc-chequing"
  assert s.account_type == "chequing"
  assert s.account_number == "05172-5163878"
  assert (s.period_start, s.period_end) == (date(2025, 12, 15), date(2026, 1, 14))
  assert [(line.date, line.amount_cents, line.description) for line in s.lines] == [
    (date(2025, 12, 16), 250000, "Payroll Deposit ACME"),
    # date column only printed once per day
    (date(2025, 12, 16), -435, "Interac purchase - COFFEE"),
    # january rolls into the next year
    (date(2026, 1, 3), -12000, "e-Transfer sent"),
  ]


def test_savings_detected():
  pdf = chequing_pdf(
    "Your RBC personal savings account statement",
    "From March 1, 2026 to March 31, 2026",
    [("2 Mar", "Interest", None, "1.23")],
  )

  s = parsers.parse(pdf)

  assert s.parser == "rbc-savings"
  assert s.account_type == "savings"
  assert [line.amount_cents for line in s.lines] == [123]


def test_visa():
  rows = [
    (40, 40, "RBC Visa Classic Low Rate"),
    (40, 55, "STATEMENT FROM DEC 20, 2025 TO JAN 19, 2026"),
    (40, 70, "4516 12** **** 9876"),
  ]
  y = 120
  for tx_date, posted, description, amount in [
    ("DEC 21", "DEC 22", "GROCERY STORE 74500015355000000000012", "$84.20"),
    ("JAN 02", "JAN 03", "PAYMENT - THANK YOU", "-$500.00"),
  ]:
    rows += [(15, y, tx_date), (15, y + 10, posted), (80, y, description), (500, y, amount)]
    y += 30

  s = parsers.parse(make_pdf(rows))

  assert s.parser == "rbc-visa"
  assert s.account_type == "credit_card"
  assert s.account_number == "9876"
  assert (s.period_start, s.period_end) == (date(2025, 12, 20), date(2026, 1, 19))
  assert [(line.date, line.posting_date, line.amount_cents, line.description) for line in s.lines] == [
    (date(2025, 12, 21), date(2025, 12, 22), -8420, "GROCERY STORE"),
    (date(2026, 1, 2), date(2026, 1, 3), 50000, "PAYMENT - THANK YOU"),
  ]


def test_visa_line_strips_reference_code():
  line = rbc_visa.parse_line("SEP 16 SEP 17 COFFEE 12345678901234567890123 $4.50", date(2025, 9, 1))
  assert line is not None
  assert line.description == "COFFEE"
  assert line.amount_cents == -450


def test_unrecognized():
  with pytest.raises(parsers.UnrecognizedStatement):
    parsers.parse(make_pdf([(40, 40, "just some pdf")]))


def test_not_a_pdf():
  with pytest.raises(parsers.UnrecognizedStatement):
    parsers.parse(b"definitely not a pdf")
