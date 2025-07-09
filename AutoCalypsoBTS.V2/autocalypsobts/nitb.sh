#!/bin/sh

echo "DB UP"
cd /root/.osmocom/
sudo osmo-nitb  -c open-bsc.cfg -l hlr.sqlite3 -P -C --debug=DRLL:DCC:DMM:DRR:DRSL:DNM --yes-i-really-want-to-run-prehistoric-software
read e 
