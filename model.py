import datetime
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
from playhouse.db_url import connect
from pydantic import BaseModel as PydanticModel
from pydantic.utils import GetterDict

from config import settings

db = connect(settings.PEEWEE_DATABASE_URL)


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
    :return:
    """
    db.create_tables([FinancialData])


if __name__ == "__main__":
    prepare_database()
