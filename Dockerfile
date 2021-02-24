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

# install nvidia driver
RUN add-apt-repository ppa:graphics-drivers/ppa
RUN apt update
RUN apt install -y nvidia-driver-460

RUN apt install -y vulkan-utils

RUN apt install -y libgles2-mesa

RUN cd /tmp &&\
    os=ubuntu1804 &&\
    cuda=10.2.89 &&\
    apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/machine-learning/repos/${os}/x86_64/7fa2af80.pub &&\
    wget https://developer.download.nvidia.com/compute/cuda/repos/${os}/x86_64/cuda-repo-${os}_${cuda}-1_amd64.deb &&\
    dpkg -i cuda-repo-*.deb &&\
    wget https://developer.download.nvidia.com/compute/machine-learning/repos/${os}/x86_64/nvidia-machine-learning-repo-${os}_1.0.0-1_amd64.deb &&\
    dpkg -i nvidia-machine-learning-repo-*.deb &&\
    rm -rf /tmp/*.deb &&\
    apt update

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES \
        ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES \
        ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics,compat32,utility

CMD cd /nlp && jupyter notebook NLP.ipynb --allow-root --NotebookApp.iopub_data_rate_limit=1e10