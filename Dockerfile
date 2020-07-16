FROM alpine:latest

LABEL source_repository="https://github.com/sapcc/ucs-exporter.git"
RUN apk --update add python3 openssl ca-certificates bash python3-dev  git py3-pip && \
    apk --update add --virtual build-dependencies libffi-dev openssl-dev libxml2 libxml2-dev libxslt libxslt-dev build-base
RUN git config --global http.sslVerify false
RUN git clone https://github.com/sapcc/ucs-exporter.git
RUN pip3 install --upgrade pip

ADD . ucs-exporter/
RUN pip3 install --upgrade -r ucs-exporter/requirements.txt

WORKDIR ucs-exporter
#CMD ["python", "ucs-exporter.py"]
