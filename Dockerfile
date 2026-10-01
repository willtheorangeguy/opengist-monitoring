FROM python:3.13-alpine

RUN apk add --no-cache git
WORKDIR /app
COPY src/opengist_exporter.py /app/opengist_exporter.py

EXPOSE 9179
ENTRYPOINT ["python3", "/app/opengist_exporter.py"]
