FROM python:3.6

WORKDIR /app

COPY requirements.txt dev-requirements.txt ./

RUN pip install -r requirements.txt -r dev-requirements.txt

COPY . ./