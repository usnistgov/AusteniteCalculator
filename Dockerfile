#FROM gsas:latest
FROM --platform=linux/amd64 ubuntu:20.04

# Install Apt packages for Python
RUN apt-get update

# new commands attempt
RUN apt install curl -y
RUN apt install libglu1-mesa-dev freeglut3-dev mesa-common-dev -y
RUN printf 'y\n12\n5' | apt install libgtk2.0-0
RUN curl https://subversion.xray.aps.anl.gov/admin_pyGSAS/downloads/gsas2full-Latest-Linux-x86_64.sh > /tmp/gsas2full-Latest-Linux-x86_64.sh
RUN bash /tmp/gsas2full-Latest-Linux-x86_64.sh -b -p ~/g2full

# project folder
RUN mkdir /root/AustCalc
COPY ./ /root/AustCalc/
RUN /root/g2full/bin/pip install -r /root/AustCalc/requirements.txt

WORKDIR /root/AustCalc/app/

EXPOSE 8050

CMD ["/root/g2full/bin/gunicorn","-w","1","-b", "0.0.0.0:8050","app:server"]