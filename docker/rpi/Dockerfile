FROM resin/raspberry-pi-python:3.6.1-slim
LABEL maintainer="post@jonathanschwarze.de"

WORKDIR /usr/src/app
RUN apt-get update -y 
COPY . .
RUN pip install -r requirements.txt && python setup.py install

EXPOSE 9500
ENTRYPOINT ["bme280_exporter"]