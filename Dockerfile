FROM ubuntu:24.04

# 시스템 시간대 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    python3-pip \
    python3-dev \
    wget \
    make \
    sudo

# pyenv 설치
RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv

# pyenv 환경변수 설정
ENV PYENV_ROOT=/root/.pyenv
ENV PATH=$PYENV_ROOT/bin:$PATH

# pyenv 초기화
RUN echo 'eval "$(pyenv init --path)"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc && \
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

# pyenv를 통해 Python 설치
RUN . ~/.bashrc && \
    pyenv install 3.13.2 && \
    pyenv global 3.13.2

# pip 업그레이드 및 필요한 패키지 설치
RUN . ~/.bashrc && \
    pip install --upgrade pip && \
    pip install pipenv uvicorn fastapi

# 작업 디렉토리 설정
WORKDIR /app

# 포트 설정
EXPOSE 8000
