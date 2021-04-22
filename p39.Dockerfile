FROM python:3.9

WORKDIR /app
COPY . ./
RUN pip install -U pip
RUN pip install .