FROM python:3.8

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		libgl1-mesa-glx \
		libgdal-dev 

ADD tiler/requirements.txt /tiler/requirements.txt
ARG CPLUS_INCLUDE_PATH=/usr/include/gdal
ARG C_INCLUDE_PATH=/usr/include/gdal
RUN pip3 install --no-cache-dir -r /tiler/requirements.txt 

RUN useradd -u 1000 uwsgi
COPY tiler/uwsgi.ini /etc/
#RUN chown uwsgi:uwsgi /mnt/data

ADD tiler /tiler
USER 1000
CMD uwsgi --ini /etc/uwsgi.ini


