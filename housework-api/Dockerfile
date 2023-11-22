FROM python:3.10

RUN apt-get update \
    && apt-get -y install libpq-dev gcc;

RUN pip install "poetry==1.7.1"

COPY . /app/housework-api/

WORKDIR /app/housework-api/

RUN poetry install
RUN poetry add psycopg2
