import asyncio
import datetime
import platform
from decimal import Decimal
from typing import Any

from peewee import (
    CompositeKey,
    DateField,
    DecimalField,
    IntegerField,
    Model,
    ModelSelect,
    TextField,
)
from peewee_async import Manager, PostgresqlDatabase
from playhouse.db_url import parse
from pydantic import BaseModel as PydanticModel
from pydantic.utils import GetterDict

from config import settings

# Adjust event loop if running on Windows machine
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

db = PostgresqlDatabase(**parse(settings.PEEWEE_POSTGRES_URL))
objects = Manager(db)


class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        res = getattr(self._obj, key, default)
        if isinstance(res, ModelSelect):
            return list(res)
        return res


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

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


def prepare_database() -> None:
    """
    Creates missing tables in the database
    """
    db.create_tables([FinancialData])


if __name__ == "__main__":
    prepare_database()
