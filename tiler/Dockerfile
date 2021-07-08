FROM python:3.8

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
		libgl1-mesa-glx \
		libgdal-dev 

#RUN useradd -u 1000 uwsgi
#RUN chown uwsgi:uwsgi /mnt/data
#USER 1000


ADD tiler/requirements.txt /root/tiler/requirements.txt
ARG CPLUS_INCLUDE_PATH=/usr/include/gdal
ARG C_INCLUDE_PATH=/usr/include/gdal
RUN pip3 install --no-cache-dir -r /root/tiler/requirements.txt 
ADD tiler /root/tiler


