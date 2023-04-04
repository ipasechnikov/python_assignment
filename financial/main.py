# isort: off
#
# Dirty hack to make parent modules importable
# There is better solution to this problem by rearranging models, but I try to
# keep directory structure as close to the task description as possible
import math
import sys
sys.path.append('../python_assignment')
# isort: on

import datetime

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, NonNegativeInt, PositiveInt

from config import settings
from model import FinancialData, FinancialDataModel

app = FastAPI()


class FinancialDataPagination(BaseModel):
    count: NonNegativeInt
    page: PositiveInt
    limit: NonNegativeInt
    pages: PositiveInt


class FinancialDataInfo(BaseModel):
    error: str = ''


class FinancialDataResponse(BaseModel):
    data: list[FinancialDataModel]
    pagination: FinancialDataPagination
    info: FinancialDataInfo


@app.get("/financial_data/")
async def financial_data(
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        symbol: str | None = None,
        limit: int = 5,
        page: int = 1
) -> FinancialDataResponse:
    try:
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
        data_page = [FinancialDataModel.from_orm(fd) for fd in query.paginate(page, limit)]

        # Build pagination structure
        count = query.count()
        pages = math.ceil(count / limit) or 1
        pagination = FinancialDataPagination(
            count=count,
            page=page,
            limit=limit,
            pages=pages
        )

        # Build response structure
        return FinancialDataResponse(
            data=data_page,
            pagination=pagination,
            info=FinancialDataInfo()
        )
    except Exception as e:
        return FinancialDataResponse(
            data=[],
            pagination=FinancialDataPagination(
                count=0,
                page=1,
                limit=limit,
                pages=1
            ),
            info=FinancialDataInfo(
                error=str(e)
            )
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.FINANCIAL_API_PORT)
