FROM python:3.12.3-slim

ENV PYTHONUNBUFFERED=1

RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY poetry.lock pyproject.toml /
RUN pip install poetry==1.3.2 \
  && poetry config virtualenvs.create false \
  && poetry install --no-root

WORKDIR /messanger_bridge

COPY ./messanger_bridge /messanger_bridge
