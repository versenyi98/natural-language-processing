#!/bin/bash

set -ex

sudo apt-get -y update

sudo apt-get install -y build-essential python3.6 python3-pip python3-dev
pip3 -q install pip --upgrade
pip3 install -r requirements.txt