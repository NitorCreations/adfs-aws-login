FROM python:3.7

WORKDIR /app
COPY . ./
RUN pip install -U pip pytest-cov pytest-mock mock
RUN pip install .