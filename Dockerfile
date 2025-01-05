# Base image
FROM python:3.11.7

WORKDIR /app

COPY requirements ./
RUN pip install --no-cache-dir -r requirements

COPY . .

EXPOSE 5000
