#!/bin/bash

set -ex

NLP_DIR=/nlp

cd $NLP_DIR

pip3 install -r requirements.txt
jupyter notebook --ip=127.0.0.1 --port=8888 --allow-root