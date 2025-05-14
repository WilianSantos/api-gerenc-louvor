ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim as base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1         
ENV PIPENV_VENV_IN_PROJECT=1 

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config \
    && pip install --no-cache-dir pipenv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock /app/
RUN pipenv install --deploy --system

COPY . /app/


CMD ["gunicorn", "setup.wsgi:application", "--bind", "0.0.0.0:8000"]
