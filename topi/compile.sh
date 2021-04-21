#!/bin/sh

gcc -shared -o lib.so -fPIC C_Backend/sync_rx_meta.c C_Backend/example_common.c -IC_Backend/include -lbladeRF -lpthread -o C_Backend/lib.so
