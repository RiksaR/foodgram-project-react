FROM python:3.8.6-slim

WORKDIR /app

COPY requirements.txt .

# RUN apt update
# RUN apt upgrade -y
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
