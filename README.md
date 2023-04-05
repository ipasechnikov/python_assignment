# Financial Data API

This is a small service that you can utilize to get latest financial data and run some statistics queries on it.

## Table of Contents

- [Financial Data API](#financial-data-api)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Local Setup (Development)](#local-setup-development)
    - [Docker Setup (Production)](#docker-setup-production)
    - [How to get the latest data from AlphaVantage](#how-to-get-the-latest-data-from-alphavantage)
  - [Built With](#built-with)

## Getting Started

There are two main ways to run the service. First one is a classical local setup that you should probably mostly use for development purposes only.
And the second one is running a service as a Docker container, which should be your preferred way of deployment.

### Local Setup (Development)

1. Get yourself a local version of PostgreSQL database. You can install it from official website or run it in a Docker. Whatever suits you the most.
   I prefer running it in a Docker. Use the following command to run a basic PostgreSQL container.

   ```commandline
   docker run --name some-postgres -e POSTGRES_PASSWORD=postgres -d postgres
   ```

2. Get Python 3.11.2 from official website or some other way. I recommend using [pyenv](https://github.com/pyenv/pyenv)
3. Install poetry to manage virtual environments. You can find how to install it [here](https://python-poetry.org/docs/#installation).
   And don't forget to add it to your `PATH`
4. Go to the project root directory
5. Run `poetry install` to install all dependencies
6. Make a copy of `.env` file by running `cp .env.example .env`
7. Get your AlphaVantage free API key [here](https://www.alphavantage.co/support/#api-key)
8. Update `ALPHA_VANTAGE_API_KEY` variable with your key in `.env` file
9. Update `PEEWEE_POSTGRES_URL` variable in `.env` file. Change `db` host to `localhost`
10. Run `poetry run financial/main.py` to start API service
11. Test it by navigating to `http://localhost:5000/financial_data/` in your browser
12. Or you can use FastAPI automatic interactive documentation available at `http://localhost:5000/docs`

### Docker Setup (Production)

1. Make a copy of `.env` file by running `cp .env.example .env`. You don't even have to change anything in it
2. Get your AlphaVantage free API key [here](https://www.alphavantage.co/support/#api-key)
3. Update `ALPHA_VANTAGE_API_KEY` variable with your key in `.env` file
4. Run `docker-compose up` to start both PostgreSQL and API service
5. Test it by navigating to `http://localhost:5000/financial_data/` in your browser 
6. Or you can use FastAPI automatic interactive documentation available at `http://localhost:5000/docs`

### How to get the latest data from AlphaVantage

If you are using Poetry, then you should run the following command from the project root directory

```commandline
poetry run python get_raw_data.py
```

If you are using Docker, then you should jump into the container and run the following command from the project root directory 

```commandline
python get_raw_data.py
```

## Built With

- [Poetry](https://python-poetry.org/)
- [pyenv](https://github.com/pyenv/pyenv)
- [mypy](https://mypy-lang.org/)
- [isort](https://pycqa.github.io/isort/)
- [peewee](https://docs.peewee-orm.com/en/latest/)
- [peewee-async](https://peewee-async.readthedocs.io/en/latest/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Requests](https://requests.readthedocs.io/en/latest/)
- [PostgreSQL](https://www.postgresql.org/)
