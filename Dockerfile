FROM python:3.13.2-slim

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
    wget \
    make \
    sudo \
    python3-venv # 가상 환경을 위한 패키지

# 가상 환경 생성
RUN python3 -m venv /venv

# 가상 환경 활성화
ENV PATH="/venv/bin:$PATH"

# pip 업그레이드 및 필요한 패키지 설치
RUN pip install --upgrade pip && \
    pip install uvicorn fastapi sqlalchemy python-multipart

WORKDIR /root/apiserver/

RUN mkdir /root/apiserver/temp

COPY database.py /root/apiserver/database.py
COPY main.py /root/apiserver/main.py
COPY models.py /root/apiserver/models.py

# 포트 설정
EXPOSE 8000

# 기본 실행 명령어
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]
