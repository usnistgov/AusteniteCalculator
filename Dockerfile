#FROM gsas:latest
FROM --platform=linux/amd64 ubuntu:20.04

# Install Apt packages for Python
RUN apt-get update -y
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# curl, c++ toolchain, gsas
RUN apt-get install curl -y
RUN apt-get install build-essential -y
RUN apt-get install libglu1-mesa-dev -y 
RUN apt-get install freeglut3-dev -y 
RUN apt-get install mesa-common-dev -y
RUN printf %s 'y\n12\n5\n' | apt-get install libgtk2.0-0
RUN curl https://subversion.xray.aps.anl.gov/admin_pyGSAS/downloads/gsas2full-Latest-Linux-x86_64.sh > /tmp/gsas2full-Latest-Linux-x86_64.sh
RUN bash /tmp/gsas2full-Latest-Linux-x86_64.sh -b -p ~/g2full

# project folder
RUN mkdir /root/AustCalc
COPY ./requirements.txt /root/AustCalc/requirements.txt
RUN /root/g2full/bin/pip install -r /root/AustCalc/requirements.txt
RUN ~/g2full/bin/python3 -c "import cmdstanpy; cmdstanpy.install_cmdstan()"
COPY ./ /root/AustCalc/

WORKDIR /root/AustCalc/

EXPOSE 8050

# flask (for dev)
CMD ["/root/g2full/bin/python3","app.py"]

# gunicorn (for prod)
# CMD ["/root/g2full/bin/gunicorn","-w","1","-b", "0.0.0.0:8050","app:server"] 
