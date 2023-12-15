FROM python:3.9.16-slim-buster

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && poetry install --no-root

COPY . .

ENTRYPOINT ["poetry", "run", "python", "xls2csv/xls2csv.py"]
