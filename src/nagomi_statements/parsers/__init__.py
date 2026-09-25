from . import rbc_chequing, rbc_visa
from .common import Line, Pdf, Statement, UnrecognizedStatement

__all__ = ["Line", "Statement", "UnrecognizedStatement", "parse"]


def parse(data: bytes) -> Statement:
  pdf = Pdf(data)
  text = pdf.text()

  # chequing first: its statements can mention visa in promo text
  if kind := rbc_chequing.detect(text):
    return rbc_chequing.parse(pdf, kind)
  if rbc_visa.detect(text):
    return rbc_visa.parse(pdf)

  raise UnrecognizedStatement("not a supported statement (supported: RBC chequing, savings, visa)")
