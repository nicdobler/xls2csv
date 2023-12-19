FROM python:3.12.1-slim

WORKDIR /app

COPY pyproject.toml poetry.lock run.sh ./

RUN pip install poetry && poetry install --no-root

COPY . .

ENTRYPOINT [ "/bin/bash", "run.sh" ]
