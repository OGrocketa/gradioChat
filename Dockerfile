FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/opt/poetry/bin:$PATH"

COPY pyproject.toml poetry.lock ./

RUN curl -sSL https://install.python-poetry.org | python3 -

    RUN --mount=type=cache,target=/root/.cache \
    for i in 1 2 3; do \
        poetry install --no-root && break;\
    done

COPY . .

EXPOSE 7860

CMD ["poetry", "run", "python", "main.py"]
