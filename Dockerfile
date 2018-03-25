FROM python:3.4-alpine
LABEL maintainer="edgarfelizmenio@gmail.com"

ADD . /code
WORKDIR /code

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

RUN pip3 freeze

RUN mkdir -p /code/input
RUN mkdir -p /code/data

ENTRYPOINT [ "/bin/sh" ]