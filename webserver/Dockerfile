FROM python:3.8

RUN apt-get update --fix-missing && \
	apt-get install -y --no-install-recommends \
		vim

ADD webserver/requirements.txt /root/webserver/requirements.txt
WORKDIR /root/webserver
RUN pip3 install --no-cache-dir -r requirements.txt
ADD webserver /root/webserver
