FROM python:2.7

WORKDIR /app
COPY . ./
RUN pip install -U pip
RUN pip install .