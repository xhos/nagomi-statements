from google.type import date_pb2 as _date_pb2
from nagomi.v1 import enums_pb2 as _enums_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ParseStatementRequest(_message.Message):
    __slots__ = ("pdf_data",)
    PDF_DATA_FIELD_NUMBER: _ClassVar[int]
    pdf_data: bytes
    def __init__(self, pdf_data: _Optional[bytes] = ...) -> None: ...

class ParseStatementResponse(_message.Message):
    __slots__ = ("statement",)
    STATEMENT_FIELD_NUMBER: _ClassVar[int]
    statement: ParsedStatement
    def __init__(self, statement: _Optional[_Union[ParsedStatement, _Mapping]] = ...) -> None: ...

class ParsedStatement(_message.Message):
    __slots__ = ("parser", "bank", "account_type", "account_number", "period_start", "period_end", "currency", "opening_balance_cents", "closing_balance_cents", "lines")
    PARSER_FIELD_NUMBER: _ClassVar[int]
    BANK_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PERIOD_START_FIELD_NUMBER: _ClassVar[int]
    PERIOD_END_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    OPENING_BALANCE_CENTS_FIELD_NUMBER: _ClassVar[int]
    CLOSING_BALANCE_CENTS_FIELD_NUMBER: _ClassVar[int]
    LINES_FIELD_NUMBER: _ClassVar[int]
    parser: str
    bank: str
    account_type: _enums_pb2.AccountType
    account_number: str
    period_start: _date_pb2.Date
    period_end: _date_pb2.Date
    currency: str
    opening_balance_cents: int
    closing_balance_cents: int
    lines: _containers.RepeatedCompositeFieldContainer[ParsedStatementLine]
    def __init__(self, parser: _Optional[str] = ..., bank: _Optional[str] = ..., account_type: _Optional[_Union[_enums_pb2.AccountType, str]] = ..., account_number: _Optional[str] = ..., period_start: _Optional[_Union[_date_pb2.Date, _Mapping]] = ..., period_end: _Optional[_Union[_date_pb2.Date, _Mapping]] = ..., currency: _Optional[str] = ..., opening_balance_cents: _Optional[int] = ..., closing_balance_cents: _Optional[int] = ..., lines: _Optional[_Iterable[_Union[ParsedStatementLine, _Mapping]]] = ...) -> None: ...

class ParsedStatementLine(_message.Message):
    __slots__ = ("date", "posting_date", "amount_cents", "direction", "description")
    DATE_FIELD_NUMBER: _ClassVar[int]
    POSTING_DATE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_CENTS_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    date: _date_pb2.Date
    posting_date: _date_pb2.Date
    amount_cents: int
    direction: _enums_pb2.TransactionDirection
    description: str
    def __init__(self, date: _Optional[_Union[_date_pb2.Date, _Mapping]] = ..., posting_date: _Optional[_Union[_date_pb2.Date, _Mapping]] = ..., amount_cents: _Optional[int] = ..., direction: _Optional[_Union[_enums_pb2.TransactionDirection, str]] = ..., description: _Optional[str] = ...) -> None: ...
