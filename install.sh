#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd $DIR

git clone https://github.com/Nuand/bladeRF.git

cd $DIR/bladeRF

mkdir -p build

cd $DIR/bladeRF/build

cmake ../

make

sudo make install

echo "/usr/local/lib" > /etc/ld.so.conf.d/usrlocallib.conf

sudo ldconfig

mkdir $DIR/images

cd $DIR/images

wget https://www.nuand.com/fx3/bladeRF_fw_latest.img

wget https://www.nuand.com/fpga/hostedxA9-latest.rbf

cd $DIR/bladeRF/host/libraries/libbladeRF_bindings/python

sudo python3 setup.py install
