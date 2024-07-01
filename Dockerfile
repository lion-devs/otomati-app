FROM python:3.12.4-slim-bookworm as py-build

ARG POETRY_VERSION=1.8.3

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
COPY otomati_app /app/otomati_app
RUN touch README.md && touch LICENSE

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENV=/app/.venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install poetry==${POETRY_VERSION}

RUN poetry check
RUN poetry install -v

FROM python:3.12.4-slim-bookworm

COPY --from=py-build /app /app
WORKDIR /app

EXPOSE 8009

ENTRYPOINT ["streamlit","run","otomati_app/Home.py","--server.port=8009","--server.address=0.0.0.0"]