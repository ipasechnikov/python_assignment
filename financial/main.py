# isort: off
#
# Dirty hack to make parent modules importable
# There is better solution to this problem by rearranging models, but I try to
# keep directory structure as close to the task description as possible
import sys
sys.path.append('../python_assignment')
# isort: on

import datetime
import math
import statistics
from collections import defaultdict
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, NonNegativeInt, PositiveInt

from config import settings
from model import FinancialData, FinancialDataModel, objects

DEFAULT_LIMIT = 5
DEFAULT_PAGE = 1

app = FastAPI()

# Ensure that there are no sync calls to the database
objects.database.allow_sync = False


class Info(BaseModel):
    error: str | dict | list = ''


class FinancialDataPagination(BaseModel):
    count: NonNegativeInt
    page: PositiveInt
    limit: NonNegativeInt
    pages: PositiveInt


class FinancialDataResponse(BaseModel):
    data: list[FinancialDataModel]
    pagination: FinancialDataPagination
    info: Info = Info()


class StatisticsData(BaseModel):
    start_date: datetime.date
    end_date: datetime.date
    symbol: str
    average_daily_open_price: float
    average_daily_close_price: float
    average_daily_volume: float


class StatisticsResponse(BaseModel):
    data: StatisticsData | None = None
    info: Info = Info()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Make validation message more readable for the end-user
    reformatted_message = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(str(fl) for fl in filtered_loc)
        reformatted_message[field_string].append(msg)

    # Format all validation exceptions to match the task description format
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            dict(info=Info(error=reformatted_message))
        )
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Last chance to handle the exception if it wasn't handled
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            dict(info=Info(error=str(exc)))
        )
    )


@app.get("/financial_data/")
async def get_financial_data(
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        symbol: str | None = None,
        limit: Annotated[int, Query(ge=1)] = DEFAULT_LIMIT,
        page: Annotated[int, Query(ge=1)] = DEFAULT_PAGE
) -> FinancialDataResponse:
    # Dynamically build WHERE clause
    conditions = []

    if start_date:
        conditions.append(FinancialData.date >= start_date)

    if end_date:
        conditions.append(FinancialData.date <= end_date)

    if symbol:
        conditions.append(FinancialData.symbol == symbol)

    query = FinancialData.select()
    if conditions:
        query = query.where(*conditions)

    # Get a single page of financial data from the database
    data_page = await objects.execute(
        query.paginate(page, limit)
    )

    count = await objects.count(query)
    pages = math.ceil(count / limit) or 1
    pagination = FinancialDataPagination(
        count=count,
        page=page,
        limit=limit,
        pages=pages
    )

    return FinancialDataResponse(
        data=[FinancialDataModel.from_orm(fd) for fd in data_page],
        pagination=pagination
    )


@app.get("/statistics/")
async def get_statistics(
        start_date: datetime.date,
        end_date: datetime.date,
        symbol: str
) -> StatisticsResponse:
    query = FinancialData.select().where(
        FinancialData.date >= start_date,
        FinancialData.date <= end_date,
        FinancialData.symbol == symbol
    )

    data: list[FinancialDataModel] = await objects.execute(query)

    # Return an error in case there is no data
    # We could probably also return 0 values, it all depends on the specification paper
    if not data:
        return StatisticsResponse(
            info=Info(error="No financial data found")
        )

    # Use Python built-in statistics module to calculate average
    avg_open_price = statistics.mean((d.open_price for d in data))
    avg_close_price = statistics.mean((d.close_price for d in data))
    avg_volume = statistics.mean((d.volume for d in data))

    return StatisticsResponse(
        data=StatisticsData(
            start_date=start_date,
            end_date=end_date,
            symbol=symbol,
            average_daily_open_price=avg_open_price,
            average_daily_close_price=avg_close_price,
            average_daily_volume=avg_volume
        )
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.FINANCIAL_API_PORT)
