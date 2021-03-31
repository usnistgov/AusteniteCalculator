FROM gsas:latest

# Install Apt packages for Python
RUN apt-get update

# project folder
RUN mkdir /AustCalc
COPY requirements.txt /AustCalc
RUN /g2full/bin/pip install -r /AustCalc/requirements.txt

COPY ./ AustCalc/

WORKDIR /AustCalc/app/

EXPOSE 8050

CMD ["/g2full/bin/python","./app.py"]