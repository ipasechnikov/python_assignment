import requests
from peewee import EXCLUDED

from config import settings
from model import FinancialData, FinancialDataModel, prepare_database

LOAD_DAYS: int = 14
LOAD_SYMBOLS: list[str] = ['IBM', 'AAPL']


def load_symbols() -> None:
    for symbol in LOAD_SYMBOLS:
        load_symbol(symbol)


def load_symbol(symbol: str) -> None:
    """
    Gets the latest available financial data from AlphaVantage API.
    Please mind, this function blocks the thread
    :param symbol: Symbol to request from the server
    :return:
    """

    request_url = (f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED'
                   f'&symbol={symbol}'
                   f'&apikey={settings.ALPHA_VANTAGE_API_KEY}')

    symbol_dict = requests.get(request_url).json()
    symbol_meta = symbol_dict['Meta Data']

    # Make sure that we actually get expected symbol
    assert symbol_meta['2. Symbol'] == symbol

    insert_data: list[dict] = []
    raw_data: dict = symbol_dict['Time Series (Daily)']
    for date_str, data_dict in raw_data.items():
        insert_data.append(
            FinancialDataModel(
                symbol=symbol,
                date=date_str,
                open_price=data_dict['1. open'],
                close_price=data_dict['4. close'],
                volume=data_dict['6. volume']
            ).dict()
        )

        # Get only required number of entries
        if len(insert_data) == LOAD_DAYS:
            break

    # Another check to ensure that server has required number of entries
    assert len(insert_data) == LOAD_DAYS

    if insert_data:
        # Even though it's highly unlikely, but we upsert the data in case for some reason AlphaVantage change will
        # change past data
        FinancialData.insert_many(insert_data).on_conflict(
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
