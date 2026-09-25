from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class AccountType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACCOUNT_UNSPECIFIED: _ClassVar[AccountType]
    ACCOUNT_CHEQUING: _ClassVar[AccountType]
    ACCOUNT_SAVINGS: _ClassVar[AccountType]
    ACCOUNT_CREDIT_CARD: _ClassVar[AccountType]
    ACCOUNT_INVESTMENT: _ClassVar[AccountType]
    ACCOUNT_OTHER: _ClassVar[AccountType]
    ACCOUNT_FRIEND: _ClassVar[AccountType]

class TransactionDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIRECTION_UNSPECIFIED: _ClassVar[TransactionDirection]
    DIRECTION_INCOMING: _ClassVar[TransactionDirection]
    DIRECTION_OUTGOING: _ClassVar[TransactionDirection]

class TransactionSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRANSACTION_SOURCE_UNSPECIFIED: _ClassVar[TransactionSource]
    TRANSACTION_SOURCE_MANUAL: _ClassVar[TransactionSource]
    TRANSACTION_SOURCE_EMAIL: _ClassVar[TransactionSource]
    TRANSACTION_SOURCE_CONNECTOR: _ClassVar[TransactionSource]
    TRANSACTION_SOURCE_STATEMENT: _ClassVar[TransactionSource]
    TRANSACTION_SOURCE_SPLIT: _ClassVar[TransactionSource]

class PeriodType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PERIOD_TYPE_UNSPECIFIED: _ClassVar[PeriodType]
    PERIOD_TYPE_7_DAYS: _ClassVar[PeriodType]
    PERIOD_TYPE_30_DAYS: _ClassVar[PeriodType]
    PERIOD_TYPE_90_DAYS: _ClassVar[PeriodType]
    PERIOD_TYPE_CUSTOM: _ClassVar[PeriodType]
    PERIOD_TYPE_3_MONTHS: _ClassVar[PeriodType]
    PERIOD_TYPE_6_MONTHS: _ClassVar[PeriodType]
    PERIOD_TYPE_1_YEAR: _ClassVar[PeriodType]
    PERIOD_TYPE_ALL_TIME: _ClassVar[PeriodType]

class Granularity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GRANULARITY_UNSPECIFIED: _ClassVar[Granularity]
    GRANULARITY_DAY: _ClassVar[Granularity]
    GRANULARITY_WEEK: _ClassVar[Granularity]
    GRANULARITY_MONTH: _ClassVar[Granularity]
ACCOUNT_UNSPECIFIED: AccountType
ACCOUNT_CHEQUING: AccountType
ACCOUNT_SAVINGS: AccountType
ACCOUNT_CREDIT_CARD: AccountType
ACCOUNT_INVESTMENT: AccountType
ACCOUNT_OTHER: AccountType
ACCOUNT_FRIEND: AccountType
DIRECTION_UNSPECIFIED: TransactionDirection
DIRECTION_INCOMING: TransactionDirection
DIRECTION_OUTGOING: TransactionDirection
TRANSACTION_SOURCE_UNSPECIFIED: TransactionSource
TRANSACTION_SOURCE_MANUAL: TransactionSource
TRANSACTION_SOURCE_EMAIL: TransactionSource
TRANSACTION_SOURCE_CONNECTOR: TransactionSource
TRANSACTION_SOURCE_STATEMENT: TransactionSource
TRANSACTION_SOURCE_SPLIT: TransactionSource
PERIOD_TYPE_UNSPECIFIED: PeriodType
PERIOD_TYPE_7_DAYS: PeriodType
PERIOD_TYPE_30_DAYS: PeriodType
PERIOD_TYPE_90_DAYS: PeriodType
PERIOD_TYPE_CUSTOM: PeriodType
PERIOD_TYPE_3_MONTHS: PeriodType
PERIOD_TYPE_6_MONTHS: PeriodType
PERIOD_TYPE_1_YEAR: PeriodType
PERIOD_TYPE_ALL_TIME: PeriodType
GRANULARITY_UNSPECIFIED: Granularity
GRANULARITY_DAY: Granularity
GRANULARITY_WEEK: Granularity
GRANULARITY_MONTH: Granularity
