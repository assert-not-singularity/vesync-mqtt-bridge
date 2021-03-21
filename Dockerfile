FROM python:3.8-alpine

LABEL maintainer="github.com/assert-not-singularity"

ENV MQTT_HOST="hostname"
ENV MQTT_PORT=1883
ENV MQTT_USER="username"
ENV MQTT_PASS="password"
ENV MQTT_ROOT_TOPIC="mqtt/topic"
ENV VESYNC_USER="username"
ENV VESYNC_PASS="password"
ENV TZ="Europe/Berlin"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./app.py" ]