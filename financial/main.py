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


class FinancialDataPagination(BaseModel):
    count: NonNegativeInt = 0
    page: PositiveInt = DEFAULT_PAGE
    limit: NonNegativeInt = DEFAULT_LIMIT
    pages: PositiveInt = 1


class FinancialDataInfo(BaseModel):
    error: str = ''


class FinancialDataResponse(BaseModel):
    data: list[FinancialDataModel] = []
    pagination: FinancialDataPagination = FinancialDataPagination()
    info: FinancialDataInfo = FinancialDataInfo()


# Make FastAPI validation exception format match the task description format
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            FinancialDataResponse(
                info=FinancialDataInfo(
                    error=str(exc)
                )
            ).dict()
        )
    )


@app.get("/financial_data/")
async def financial_data(
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        symbol: str | None = None,
        limit: Annotated[int, Query(ge=1)] = DEFAULT_LIMIT,
        page: Annotated[int, Query(ge=1)] = DEFAULT_PAGE
) -> FinancialDataResponse:
    try:
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

        # Build pagination structure
        count = await objects.count(query)
        pages = math.ceil(count / limit) or 1
        pagination = FinancialDataPagination(
            count=count,
            page=page,
            limit=limit,
            pages=pages
        )

        # Build response structure
        return FinancialDataResponse(
            data=[FinancialDataModel.from_orm(fd) for fd in data_page],
            pagination=pagination
        )
    except Exception as e:
        return FinancialDataResponse(
            info=FinancialDataInfo(
                error=str(e)
            )
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.FINANCIAL_API_PORT)
