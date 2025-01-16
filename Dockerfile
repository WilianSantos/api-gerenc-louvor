ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim as base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/
