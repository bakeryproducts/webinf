FROM python:3.8
#FROM ubuntu:20.04

#RUN apt-get update && \
#	apt-get install \
#		vim

ADD webserver/requirements.txt /root/webserver/requirements.txt
WORKDIR /root/webserver
RUN pip3 install --no-cache-dir -r requirements.txt
ADD webserver /root/webserver
