FROM docker.io/ubuntu:20.04

LABEL source_repository="https://github.com/sapcc/ucs-exporter.git"
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install -y python3 git \
    && apt-get install -y python3-pip
RUN git config --global http.sslVerify false
RUN git clone https://github.com/sapcc/ucs-exporter.git
RUN pip3 install --upgrade pip

ADD . ucs-exporter/
RUN pip3 install --upgrade -r ucs-exporter/requirements.txt

WORKDIR /ucs-exporter
#CMD ["python", "ucs-exporter.py"]
