import uvicorn
from fastapi import FastAPI
from config import settings

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.FINANCIAL_API_PORT)
