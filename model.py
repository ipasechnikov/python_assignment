import datetime
from decimal import Decimal

from peewee import (
    CompositeKey,
    DateField,
    DecimalField,
    IntegerField,
    Model,
    ModelSelect,
    TextField,
)
from playhouse.db_url import connect
from pydantic import BaseModel as PydanticModel

from config import settings

db = connect(settings.PEEWEE_POSTGRES_URL)


class BaseModel(Model):
    class Meta:
        database = db


class FinancialData(BaseModel):
    symbol = TextField()
    date = DateField()
    open_price = DecimalField()
    close_price = DecimalField()
    volume = IntegerField()

    class Meta:
        table_name = 'financial_data'
        primary_key = CompositeKey('symbol', 'date')


class FinancialDataModel(PydanticModel):
    symbol: str
    date: datetime.date
    open_price: Decimal
    close_price: Decimal
    volume: int


def prepare_database() -> None:
    db.create_tables([FinancialData])


if __name__ == "__main__":
    prepare_database()
