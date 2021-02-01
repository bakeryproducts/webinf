FROM python:3.6-alpine

#RUN apt-get update --fix-missing && \
#	apt-get install -y --no-install-recommends \
#		vim

ADD webserver/requirements.txt /root/webserver/requirements.txt
RUN pip3 install --no-cache-dir -r /root/webserver/requirements.txt
ADD webserver /root/webserver
