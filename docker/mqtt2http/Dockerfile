FROM python:3.10.2-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk upgrade

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./paho_client.py /opt/mqtt2http/

ENTRYPOINT python /opt/mqtt2http/paho_client.py
