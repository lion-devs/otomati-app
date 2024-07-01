FROM python:3.12.4-slim-bookworm as py-build

ARG POETRY_VERSION=1.8.3

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
COPY otomati_app /app/otomati_app
RUN touch README.md && touch LICENSE

RUN set -eux; \
    apt-get update -y && \
    apt-get install -y build-essential

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENV=/app/.venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install poetry==${POETRY_VERSION}

RUN poetry check
RUN poetry install -vvv --no-root --no-dev

FROM python:3.12.4-slim-bookworm

ENV PORT=8501
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=py-build /app /app
WORKDIR /app

EXPOSE ${PORT:-8501}

HEALTHCHECK CMD curl --fail http://localhost:$PORT/healthz || exit 1

ENV PYTHONPATH=/app

#ENTRYPOINT ["streamlit","run","otomati_app/Home.py","--server.port=${PORT:-8009}","--server.address=0.0.0.0"]
ENTRYPOINT ["sh", "-c", "streamlit run otomati_app/Home.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]