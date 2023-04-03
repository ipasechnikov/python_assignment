import requests
from peewee import EXCLUDED

from config import settings
from model import FinancialData, FinancialDataModel, prepare_database

LOAD_DAYS: int = 14


def load_symbols() -> None:
    symbols = ['IBM', 'AAPL']
    for symbol in symbols:
        load_symbol(symbol)


def load_symbol(symbol: str) -> None:
    request_url = (f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED'
                   f'&symbol={symbol}'
                   f'&apikey={settings.ALPHA_VANTAGE_API_KEY}')

    symbol_dict = requests.get(request_url).json()
    symbol_meta = symbol_dict['Meta Data']
    assert symbol_meta['2. Symbol'] == symbol

    financial_data: list[dict] = []
    symbol_data: dict = symbol_dict['Time Series (Daily)']
    for date_str, data_dict in symbol_data.items():
        financial_data.append(
            FinancialDataModel(
                symbol=symbol,
                date=date_str,
                open_price=data_dict['1. open'],
                close_price=data_dict['4. close'],
                volume=data_dict['6. volume']
            ).dict()
        )

        if len(financial_data) == LOAD_DAYS:
            break

    assert len(financial_data) == LOAD_DAYS

    if financial_data:
        FinancialData.insert_many(financial_data).on_conflict(
            conflict_target=[
                FinancialData.symbol, FinancialData.date
            ],
            update={
                FinancialData.open_price: EXCLUDED.open_price,
                FinancialData.close_price: EXCLUDED.close_price,
                FinancialData.volume: EXCLUDED.volume
            }
        ).execute()


if __name__ == "__main__":
    prepare_database()
    load_symbols()
