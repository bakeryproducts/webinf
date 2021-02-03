FROM nvcr.io/nvidia/pytorch:20.07-py3 

WORKDIR /workdir

RUN apt update 

RUN git clone https://github.com/bakeryproducts/shallow && cd shallow && pip install -e .

#COPY ./model/ /root/infer/model/

ADD infer/requirements.txt /root/infer/requirements.txt
RUN pip3 install --no-cache-dir -r /root/infer/requirements.txt 
ADD infer /root/infer
