import json
import logging
import os
import signal
import time
from concurrent import futures

import grpc
from google.type import date_pb2
from nagomi.v1 import enums_pb2, statement_parser_pb2, statement_parser_pb2_grpc

from . import parsers

log = logging.getLogger("nagomi-statements")

MAX_MESSAGE_BYTES = 32 * 1024 * 1024

ACCOUNT_TYPES = {
  "chequing": enums_pb2.ACCOUNT_CHEQUING,
  "savings": enums_pb2.ACCOUNT_SAVINGS,
  "credit_card": enums_pb2.ACCOUNT_CREDIT_CARD,
}


def _date(d) -> date_pb2.Date:
  return date_pb2.Date(year=d.year, month=d.month, day=d.day)


def to_proto(s: parsers.Statement) -> statement_parser_pb2.ParsedStatement:
  msg = statement_parser_pb2.ParsedStatement(
    parser=s.parser,
    bank=s.bank,
    account_type=ACCOUNT_TYPES.get(s.account_type, enums_pb2.ACCOUNT_UNSPECIFIED),
    account_number=s.account_number,
    period_start=_date(s.period_start),
    period_end=_date(s.period_end),
    currency=s.currency,
  )
  if s.opening_balance_cents is not None:
    msg.opening_balance_cents = s.opening_balance_cents
  if s.closing_balance_cents is not None:
    msg.closing_balance_cents = s.closing_balance_cents

  for line in s.lines:
    out = msg.lines.add(
      date=_date(line.date),
      amount_cents=abs(line.amount_cents),
      direction=enums_pb2.DIRECTION_OUTGOING if line.amount_cents < 0 else enums_pb2.DIRECTION_INCOMING,
      description=line.description,
    )
    if line.posting_date:
      out.posting_date.CopyFrom(_date(line.posting_date))
  return msg


class StatementParser(statement_parser_pb2_grpc.StatementParserServiceServicer):
  def ParseStatement(self, request, context):
    started = time.monotonic()
    try:
      statement = parsers.parse(request.pdf_data)
    except parsers.UnrecognizedStatement as e:
      log.info("unrecognized statement: %s", e)
      context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
    except Exception:
      log.exception("parse failed")
      context.abort(grpc.StatusCode.INTERNAL, "failed to parse statement")

    log.info(
      "parsed statement parser=%s period=%s..%s lines=%d took=%.0fms",
      statement.parser,
      statement.period_start,
      statement.period_end,
      len(statement.lines),
      (time.monotonic() - started) * 1000,
    )
    return statement_parser_pb2.ParseStatementResponse(statement=to_proto(statement))


class JsonFormatter(logging.Formatter):
  def format(self, record):
    entry = {"time": self.formatTime(record), "level": record.levelname.lower(), "msg": record.getMessage()}
    if record.exc_info:
      entry["error"] = self.formatException(record.exc_info)
    return json.dumps(entry)


def setup_logging():
  handler = logging.StreamHandler()
  if os.environ.get("LOG_FORMAT") == "json":
    handler.setFormatter(JsonFormatter())
  else:
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
  level = os.environ.get("LOG_LEVEL", "info").upper()
  logging.basicConfig(level="WARNING" if level == "WARN" else level, handlers=[handler])


def main():
  setup_logging()
  address = os.environ.get("LISTEN_ADDRESS", "127.0.0.1:55559")

  server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=4),
    options=[
      ("grpc.max_receive_message_length", MAX_MESSAGE_BYTES),
      ("grpc.max_send_message_length", MAX_MESSAGE_BYTES),
    ],
  )
  statement_parser_pb2_grpc.add_StatementParserServiceServicer_to_server(StatementParser(), server)
  if server.add_insecure_port(address) == 0:
    raise SystemExit(f"could not listen on {address}")
  server.start()
  log.info("listening on %s", address)

  signal.signal(signal.SIGTERM, lambda *_: server.stop(5))
  server.wait_for_termination()


if __name__ == "__main__":
  main()
