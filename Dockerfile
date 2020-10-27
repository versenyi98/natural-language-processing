FROM ubuntu:latest

RUN apt-get update && apt-get -y update

RUN apt-get install -y build-essential python3.6 python3-pip python3-dev
RUN pip3 -q install pip --upgrade

RUN pip3 install gdown
RUN apt-get -y install zip unzip

RUN pip3 install jupyter

COPY start.sh /
CMD ["/start.sh"]