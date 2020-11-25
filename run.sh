#!/bin/bash

set -eu

docker build -t nlp .
docker run --rm --runtime=runc --privileged -p 8888:8888 -v ${PWD}:/nlp --volume=/tmp/.X11-unix:/tmp/.X11-unix:rw --net=host -i -t nlp
