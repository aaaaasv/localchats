FROM python:3

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#RUN apt-get update && apt-get install -y netcat binutils libproj-dev libgdal-dev gdal-bin python-gdal python3-gdal

RUN apt update && apt install -y --no-install-recommends \
        libgdal-dev \
        gcc && \
pip install numpy==1.18.1 && \
pip install gdal==2.4.0 && \
        rm -rf /var/lib/apt/lists/*

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt


COPY entrypoint.sh .


COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
