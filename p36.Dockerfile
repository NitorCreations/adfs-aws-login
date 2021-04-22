FROM python:3.6

WORKDIR /app
COPY . ./
RUN pip install -U pip
RUN pip install .