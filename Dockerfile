ARG PYTHON=3.12

FROM python:${PYTHON}-slim

RUN apt update
RUN apt install -y git nano less curl

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="${PATH}:${POETRY_HOME}/bin"
RUN curl -sSL https://install.python-poetry.org | python -

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY . /app

# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "app.py"]
