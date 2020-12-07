FROM ubuntu:latest

RUN apt-get -y update

RUN apt-get install -y build-essential python3.6 python3-pip python3-dev
RUN pip3 -q install pip --upgrade

COPY start.sh /
CMD ["/start.sh"]