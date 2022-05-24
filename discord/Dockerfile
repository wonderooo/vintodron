FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt
RUN mkdir /app
COPY ./dc.py /app
COPY ./.env /app
WORKDIR /app
