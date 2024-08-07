FROM python:3.12.1-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && poetry install --no-root

COPY xls2csv ./xls2csv

ENTRYPOINT [ "poetry", "run", "python", "xls2csv/xls2csv.py", "/inout" ]
