FROM python:3.11

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && \
    poetry install && \
    poetry cache clear --all pypi --no-interaction

COPY . /app

CMD ["python", "-m", "src.app.bot"]
