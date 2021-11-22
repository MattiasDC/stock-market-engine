FROM python:3.9-slim-buster

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && apt-get purge -y --auto-remove 

RUN mkdir -p /app

# set working directory
WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip

COPY setup.py .
COPY pyproject.toml .
COPY setup.cfg .

COPY ./stock_market_engine ./stock_market_engine

RUN pip install -e . --no-cache-dir

EXPOSE 8000
CMD ["uvicorn", "stock_market_engine.main:app", "--host", "0.0.0.0", "--lifespan=on", "--use-colors", "--reload"]