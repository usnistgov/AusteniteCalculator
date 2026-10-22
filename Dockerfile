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

# --- Security: patch vulnerable packages shipped inside the GSAS-II (g2full)
# environment. These are NOT installed via requirements.txt; the g2full
# installer bundles its own Python env with outdated packages that Trivy flags
# (HIGH/CRITICAL). Pin to the minimum fixed versions. Keep this list in sync
# with the Trivy scan — revisit when the GSAS-II bundle is updated.
RUN /root/g2full/bin/pip install --upgrade \
    "GitPython>=3.1.59" \
    "pillow>=13.0.0" \
    "certifi>=2026.10.19" \
    "Brotli>=1.2.0" \
    "urllib3>=2.6.0" \
    "setuptools>=70.0.0" \
    "tornado>=6.4.2" \
    "wheel>=0.46.2"

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
# -w 4: the app is now concurrency-safe (each request isolates its input/work/output
# files in a per-request temp dir), so multiple workers no longer cross-contaminate
# user data. Each worker runs a heavy GSAS-II peak fit + Stan MCMC, so this is CPU/
# memory intensive — size worker count to the host, and ensure FLASK_SECRET_KEY is
# set in the environment so session cookies (used by /download) work across workers.
CMD ["/root/g2full/bin/gunicorn","-w","4","-b","0.0.0.0:8050","app:app"]
