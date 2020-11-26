#!/bin/bash

set -ex

NLP_DIR=$PWD
DATA_DIR=$NLP_DIR/Data

sudo apt-get -y update

sudo apt-get install -y build-essential python3.6 python3-pip python3-dev
pip3 -q install pip --upgrade

pip3 install -r requirements.txt

if [ ! -d "$DATA_DIR" ] || [ -z "$(ls -A $DATA_DIR)" ]; then
    mkdir -p $DATA_DIR
    cd $DATA_DIR

    gdown https://drive.google.com/uc?id=1k7GfVRqrHFK00ABkit0oGQo62fCakMSZ -O data.zip

    unzip data.zip

    rm data.zip

    cd $NLP_DIR
fi
