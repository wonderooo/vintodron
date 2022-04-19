FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" > /etc/apk/repositories
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories
RUN apk update
RUN apk add gcc py3-cffi libffi-dev libc-dev linux-headers chromium chromium-chromedriver xvfb

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
COPY ./.env /app
COPY ./selenium_scrap.py /app
WORKDIR /app
