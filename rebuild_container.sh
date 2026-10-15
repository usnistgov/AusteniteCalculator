#!/bin/sh

sudo docker rm -f aust_calc
sudo docker build -t ac -f Dockerfile_prod .
sudo docker image prune -f
sudo docker run -d -p 8081:8050 --name aust_calc ac