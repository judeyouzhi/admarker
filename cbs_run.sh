#!/usr/bin/env bash

rm -f predict.csv

touch predict.csv

rm -rf cbs_serving

mkdir cbs_serving

python predicting.py https://cbsnhls-i.akamaihd.net/hls/live/264710/cbsn_hlsprod_2/master_360.m3u8 cbs_serving

#while true; do    cp output.m3u8 /var/www/html/m3u8/;    sleep 6; done

