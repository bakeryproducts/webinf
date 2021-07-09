#FROM python:3.6-alpine
FROM python:3.8

#RUN apt-get update 

ADD webserver/requirements.txt /webserver/requirements.txt
WORKDIR /webserver
RUN pip3 install --no-cache-dir -r requirements.txt
ADD webserver /webserver
