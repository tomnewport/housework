FROM python:3.10

RUN pip install "poetry==$POETRY_VERSION"

COPY . /app/housework-api/

WORKDIR /app/housework-api/

RUN poetry install
