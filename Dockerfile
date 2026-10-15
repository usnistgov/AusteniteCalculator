#FROM gsas:latest
FROM ubuntu:20.04

# Install Apt packages for Python
RUN apt-get update -y && \
    echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# curl, c++ toolchain, gsas — consolidated into single layer
RUN apt-get install --no-install-recommends -y \
    nano \
    curl \
    ca-certificates \
    build-essential \
    libtbb-dev \
    libglu1-mesa-dev \
    freeglut3-dev \
    mesa-common-dev \
    libgtk2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/AdvancedPhotonSource/GSAS-II-buildtools/releases/download/v1.0.1/old_gsas2full-5786-Linux-x86_64.sh > /tmp/g2full.sh && \
    bash /tmp/g2full.sh -b -p ~/g2full && \
    rm /tmp/g2full.sh

# project folder
RUN mkdir /root/AustCalc
COPY ./requirements.txt /root/AustCalc/requirements.txt
RUN /root/g2full/bin/pip install -r /root/AustCalc/requirements.txt
RUN ~/g2full/bin/python3 -c "import cmdstanpy; cmdstanpy.install_cmdstan()"
COPY ./ /root/AustCalc/

# compile stan — use dynamic path instead of hardcoded version
RUN CMDSTAN_DIR=$(ls -d /root/.cmdstan/cmdstan-*/ | head -1) && \
    echo "Using CmdStan at: $CMDSTAN_DIR" && \
    cd "$CMDSTAN_DIR" && \
    make /root/AustCalc/stan_files/one_sample && \
    make /root/AustCalc/stan_files/multiple_samples

WORKDIR /root/AustCalc/app/

RUN rm -rf /root/AustCalc/server_datadir /root/AustCalc/server_workdir && \
    mkdir /root/AustCalc/server_datadir /root/AustCalc/server_workdir

EXPOSE 8050

# flask (for dev)
# CMD ["/root/g2full/bin/python3","app.py"]

# gunicorn (for prod)
CMD ["/root/g2full/bin/gunicorn","-w","1","-b","0.0.0.0:8050","app:app"]
