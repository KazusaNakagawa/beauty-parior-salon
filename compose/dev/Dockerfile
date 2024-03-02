FROM ubuntu:22.04

ENV PYTHON_VERSION=3.12.1

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev \
    mysql-client \
    sudo \
    vim \
    wget \
    zlib1g-dev

# root権限意外でも扱えるようにする 共有サーバとか
WORKDIR /opt

# https://phoenixnap.com/kb/how-to-install-python-3-ubuntu
RUN wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz && \
    tar -xf Python-$PYTHON_VERSION.tgz && \
    rm -f Python-$PYTHON_VERSION.tgz

WORKDIR /opt/Python-$PYTHON_VERSION

RUN ./configure && \
    make && \
    make install
#
ENV PATH /opt/python/bin:$PATH
#
COPY ./requirements/dev.txt ./
RUN pip3 install --upgrade pip && \
    pip3 install -r dev.txt

COPY . .

WORKDIR /work
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
