# isort: off
#
# Dirty hack to make config.py importable
# There is better solution to this problem by rearranging models, but I try to
# keep directory structure as close to the task description as possible
import sys
sys.path.append('../python_assignment')
# isort: on

import uvicorn
from fastapi import FastAPI

from config import settings

app = FastAPI()


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.FINANCIAL_API_PORT)
