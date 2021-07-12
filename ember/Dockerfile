FROM python:3.8


ADD ember/requirements.txt /ember/requirements.txt
WORKDIR /ember
RUN pip3 install --no-cache-dir -r requirements.txt
ADD ember /ember
