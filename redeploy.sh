#!/bin/sh

set -e

rm master.zip
rm -rf master

wget https://github.com/usnistgov/AusteniteCalculator/archive/refs/heads/master.zip
unzip master.zip

sudo docker build -t ac ./AusteniteCalculator-master
sudo docker rm -f $(sudo docker ps -a -q)
sudo docker image prune -f
sudo docker run -d -p 80:8050 ac
