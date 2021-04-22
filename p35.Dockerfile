FROM python:3.5

WORKDIR /app
COPY . ./
RUN pip install -U pip
RUN pip install .