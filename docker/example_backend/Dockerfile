# pull official base image
FROM python:3.8-buster

# set work directory
WORKDIR /usr/src/example_backend

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# base updates
RUN apt-get update && apt-get upgrade -y

# important utils
RUN apt-get install -y curl apt-utils netcat

# upgrade pip
RUN pip install --upgrade pip

# install django dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/example_backend/entrypoint.sh"]