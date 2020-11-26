#!/bin/bash

set -ex

NLP_DIR=/nlp
DATA_DIR=$NLP_DIR/Data

cd $NLP_DIR

pip3 install -r requirements.txt

if [ ! -d "$DATA_DIR" ] || [ -z "$(ls -A $DATA_DIR)" ]; then
    mkdir -p $DATA_DIR
    cd $DATA_DIR

    gdown https://drive.google.com/uc?id=1k7GfVRqrHFK00ABkit0oGQo62fCakMSZ -O data.zip

    unzip data.zip

    rm data.zip

    cd $NLP_DIR
fi

jupyter notebook --ip=127.0.0.1 --port=8888 --allow-root