#FROM gsas:latest
FROM ubuntu:20.04

# Install Apt packages for Python
RUN apt-get update -y
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# curl, c++ toolchain, gsas
RUN apt-get install nano -y
RUN apt-get install curl -y
RUN apt-get install build-essential -y
RUN apt-get install libtbb-dev -y
RUN apt-get install libglu1-mesa-dev -y 
RUN apt-get install freeglut3-dev -y 
RUN apt-get install mesa-common-dev -y
RUN printf %s 'y\n12\n5\n' | apt-get install libgtk2.0-0
RUN curl -L https://github.com/AdvancedPhotonSource/GSAS-II-buildtools/releases/download/v1.0.1/old_gsas2full-5786-Linux-x86_64.sh > /tmp/g2full.sh
RUN bash /tmp/g2full.sh -b -p ~/g2full

# project folder
RUN mkdir /root/AustCalc
COPY ./requirements.txt /root/AustCalc/requirements.txt
RUN /root/g2full/bin/pip install -r /root/AustCalc/requirements.txt
RUN ~/g2full/bin/python3 -c "import cmdstanpy; cmdstanpy.install_cmdstan()"
COPY ./ /root/AustCalc/

# compile stan (in case of a different operating system)
# DOES NOT CURRENTLY WORK
# Fragile to version number
RUN cd /root/.cmdstan/cmdstan-2.39.0/
RUN make ~/AustCalc/stan_files/one_sample
RUN make ~/AustCalc/stan_files/multiple_samples

WORKDIR /root/AustCalc/app/

RUN rm -r /root/AustCalc/server_datadir
RUN rm -r /root/AustCalc/server_workdir

RUN mkdir /root/AustCalc/server_datadir
RUN mkdir /root/AustCalc/server_workdir

EXPOSE 8050

# flask (for dev)
# CMD ["/root/g2full/bin/python3","app.py"]

# gunicorn (for prod)
CMD ["/root/g2full/bin/gunicorn","-w","1","-b", "0.0.0.0:8050","app:app"] 
