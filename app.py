from typing import Any
from pyvesync import VeSync

import paho.mqtt.client as mqtt
import os
import time

class App:

    MQTT_ROOT_TOPIC = os.environ["MQTT_ROOT_TOPIC"]

    _manager = VeSync
    _purifier = Any

    _auto_mode = False
    _publishing = False
    _run = True

    def __init__(self):
        self.main()

    def main(self):
        # Connect to MQTT broker
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        print("Connecting to MQTT broker...")
        client.username_pw_set(os.environ["MQTT_USER"], os.environ["MQTT_PASS"])
        client.connect(os.environ["MQTT_HOST"], port=int(os.environ["MQTT_PORT"]), keepalive=60)

        client.subscribe(f"{self.MQTT_ROOT_TOPIC}/power_state")
        client.subscribe(f"{self.MQTT_ROOT_TOPIC}/auto_mode")
        # client.subscribe(f"{self.MQTT_ROOT_TOPIC}/sleep_mode")
        client.subscribe(f"{self.MQTT_ROOT_TOPIC}/fan_speed")
        client.subscribe(f"{self.MQTT_ROOT_TOPIC}/air_quality")
        client.subscribe(f"{self.MQTT_ROOT_TOPIC}/filter_life")

        # Connect to VeSync API
        print("Connecting to VeSync API...")
        attempts = 3
        self._manager = VeSync(os.environ["VESYNC_USER"], os.environ["VESYNC_PASS"], os.environ["TZ"])

        while not self._manager.login() and attempts > 0:
            print(f"Could not connect. Attempts remaining: {attempts}.")
            attempts -= 1
            time.sleep(1000)

        self._manager.update()
        self._purifier = self._manager.fans[0]

        # Start loop
        client.loop_start()

        while self._run:
            try:
                # Get readings from API
                self._purifier.update()

                power_state = self._purifier.device_status
                fan_speed = self._purifier.fan_level

                # If the fan is in auto mode, the value will be returned as None
                if fan_speed == None:
                    fan_speed = 0

                air_quality = self._purifier.air_quality
                filter_life = self._purifier.filter_life
                self._auto_mode = self._purifier.mode == "auto"

                # print(f"state: {power_state}, speed: {fan_speed}, AQ: {air_quality}, life: {filter_life}, auto: {self._auto_mode}")

                self._publishing = True
                client.publish("smarthome/air-purifier/power_state", power_state.upper())
                client.publish("smarthome/air-purifier/auto_mode", "ON" if self._auto_mode else "OFF")
                client.publish("smarthome/air-purifier/fan_speed", fan_speed)
                client.publish("smarthome/air-purifier/air_quality", air_quality)
                client.publish("smarthome/air-purifier/filter_life", filter_life)
                time.sleep(0.5)
                self._publishing = False

                time.sleep(5)
            except KeyboardInterrupt:
                self._run = False

        print("Stopping application...")

        client.loop_stop()


    def on_connect(self, client, userdata, flags, rc):
        print(f"MQTT connection returned result: {mqtt.connack_string(rc)}")


    def on_message(self, client, userdata, message):
        # Don't listen to own messages > prevent message recursion
        if self._publishing:
            return

        decoded_payload = message.payload.decode("utf-8")
        print(f"Received {message.topic}: {decoded_payload}")

        if message.topic == f"{self.MQTT_ROOT_TOPIC}/power_state":
            if decoded_payload == "ON":
                self._purifier.turn_on()
            elif decoded_payload == "OFF":
                self._purifier.turn_off()

        if message.topic == f"{self.MQTT_ROOT_TOPIC}/auto_mode":
            if decoded_payload == "ON":
                self._purifier.auto_mode()
                self._auto_mode = True
            elif decoded_payload == "OFF":
                self._purifier.manual_mode()
                self._auto_mode = False

        if message.topic == f"{self.MQTT_ROOT_TOPIC}/fan_speed":
            try:
                value = int(decoded_payload)
                if value not in [1, 2, 3]:
                    return

                if self._auto_mode:
                    self._purifier.manual_mode()
                    self._auto_mode = False

                self._purifier.change_fan_speed(value)

            except ValueError:
                pass


if __name__ == "__main__":
    App()