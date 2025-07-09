#!/bin/sh

echo -e "\e[30;41m
Installing AutoCalypsoBTS.V2        
\e[0m"
sleep 3
pip3 install pyautogui >/dev/null 2>&1
sleep 3
sudo mkdir /root/.osmocom
sudo cp msisdn_changer.py /root/.osmocom/
sudo cp smpp.py /root/.osmocom/
sudo cp sms_attack.py /root/.osmocom/
sudo cp open-bsc.cfg /root/.osmocom/
sudo cp osmo-bts.cfg /root/.osmocom/
sudo cp ussd.py /root/.osmocom/
sudo cp smS.py /root/.osmocom/
sudo cp sub.py /root/.osmocom/
sudo chmod 777 autocalypsobts/console.sh autocalypsobts/nitb.sh autocalypsobts/osmobts.sh autocalypsobts/transceiver.sh autocalypsobts/trx.sh autocalypsobts/trx2.sh autocalypsobts/autobts.py
echo -e "\e[32m
Done !
\e[0m"

echo -e "\e[30;41m
If you want to  open AutoCalypsoBTS.V2 
Use : cd autocalypsobts && sudo python3 autobts.py     
\e[0m"
