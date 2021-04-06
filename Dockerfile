FROM ubuntu:latest

COPY requirements.txt ./

RUN apt update
RUN apt install -y python3-pip

RUN pip3 install -r requirements.txt
RUN pip3 install https://github.com/oroszgy/spacy-hungarian-models/releases/download/hu_core_ud_lg-0.3.1/hu_core_ud_lg-0.3.1-py3-none-any.whl  

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get install -y mesa-utils

RUN apt-get install -y software-properties-common wget

RUN add-apt-repository ppa:graphics-drivers/ppa

RUN apt-get update

ENV PATH /usr/local/cuda/bin/:$PATH
ENV LD_LIBRARY_PATH /usr/local/cuda/lib:/usr/local/cuda/lib64
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
LABEL com.nvidia.volumes.needed="nvidia_driver"

ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:/usr/local/cuda/lib64

CMD cd /nlp && jupyter notebook NLP.ipynb --allow-root --NotebookApp.iopub_data_rate_limit=1e10