#!/bin/bash

set -ex

NLP_DIR=/nlp
DATA_DIR=$NLP_DIR/Data

if [ ! -d "$DATA_DIR" ]; then
    mkdir -p $DATA_DIR
    cd $DATA_DIR

    gdown https://drive.google.com/uc?id=1k7GfVRqrHFK00ABkit0oGQo62fCakMSZ -O data.zip

    unzip data.zip

    rm data.zip
fi

cd $NLP_DIR

pip3 install -r requirements.txt
jupyter notebook --ip=127.0.0.1 --port=8888 --allow-root