FROM python:3.6-alpine

ADD labeler/requirements.txt /root/labeler/requirements.txt
RUN pip3 install --no-cache-dir -r /root/labeler/requirements.txt 
ADD labeler /root/labeler
