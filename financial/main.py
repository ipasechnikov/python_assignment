# isort: off
#
# Dirty hack to make parent modules importable
# There is better solution to this problem by rearranging models, but I try to
# keep directory structure as close to the task description as possible
import sys
sys.path.append('../python_assignment')
# isort: on

import datetime

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, NonNegativeInt, PositiveInt

from config import settings
from model import FinancialDataModel

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
    raise NotImplementedError


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.FINANCIAL_API_PORT)
