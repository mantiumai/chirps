FROM python:3.11

RUN apt-get update && \
    apt-get install -y git docker.io docker-compose

WORKDIR /app
COPY ../requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app
