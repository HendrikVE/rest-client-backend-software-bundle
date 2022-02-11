FROM python:3.10.2-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk upgrade -y

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY kafka_consumer.py /opt/kafka-consumer/

ENTRYPOINT python /opt/kafka-consumer/kafka_consumer.py
