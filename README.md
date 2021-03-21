# VeSync Air Purifier MQTT Bridge for openHAB 3

## What it is

- A quickly prototyped project to control the Levoit LV-PUR131 air purifier via openHAB 3
- A way around implementing the whole VeSync API as a binding for openHAB 3
- Another reason to have a docker daemon running somewhere in the network
- An implementation using a small part of Joe Trabulsy's [pyvesync library](https://github.com/webdjoe/pyvesync)

## What it is not

- A ripe piece of software - it's really just prototyped, use on your own risk
- A possibility to control any VeSync device using MQTT - it's really just an implementation for the air purifier

## To Dos

- [ ] error handling for MQTT and VeSync API
