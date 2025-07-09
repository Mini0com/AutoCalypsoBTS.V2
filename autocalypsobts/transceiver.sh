#!/bin/sh
#edit sudo ./transceiver -a (clock arfcn) 
#!!!!!!!!!!!!!!! use -2 key if u have 2 or more phones !!!!!!!!!!!!!!!!!!!!!!!
cd /home/osmocom/trx/src/host/layer23/src/transceiver/
echo "CLOCK"
sudo ./transceiver -a 90 -r 99
read e 
