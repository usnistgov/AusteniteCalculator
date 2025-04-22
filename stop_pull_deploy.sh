#!/bin/sh

sudo docker rm -f aust_calc
rm -r AusteniteCalculator-develop/
wget https://github.com/usnistgov/AusteniteCalculator/archive/refs/heads/develop.zip
unzip develop.zip
rm develop.zip
cd AusteniteCalculator-develop/
sudo docker build -t ac -f Dockerfile_prod .
sudo docker image prune -f
sudo docker run -d -p 8081:8050 --name aust_calc ac