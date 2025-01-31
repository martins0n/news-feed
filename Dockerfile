FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install poetry==1.6.1

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* /app/
RUN poetry install


EXPOSE 8501

RUN ["chmod", "+x", "start.sh"]

CMD ./start.sh