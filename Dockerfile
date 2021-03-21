FROM python:3.8-alpine

LABEL maintainer="github.com/assert-not-singularity"

ENV MQTT_HOST="hostname" \
    MQTT_PORT=1883 \
    MQTT_USER="username" \
    MQTT_PASS="password" \
    MQTT_ROOT_TOPIC="mqtt/topic" \
    VESYNC_USER="username" \
    VESYNC_PASS="password" \
    TZ="Europe/Berlin"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./app.py" ]