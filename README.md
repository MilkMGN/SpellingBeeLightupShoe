
# Magic Foot

Firmware for Arduinos and Raspberry Pis being used in a production of 25th Annual Putnam County Spelling Bee.

This works using:

A Raspberry Pi connected to an LX rig using sACN over Ethernet, which broadcasts (Using 5ghz radios) specific addresses as variables to 2x Arduino Nano

The arduino nanos have cables connected to them to send power & data to two shoes, and viola, "Magic Foot"!


## Authors

- [@GhastMan01012](https://www.github.com/GhastMan01012)
- [@TheExoEngineer](https://www.github.com/TheExoEngineer)
- [@MilkMGN](https://www.github.com/MilkMGN)

## Acknowledgements

 - [sACN (PyPi)](https://pypi.org/project/sacn/)
 - [nrf24 (PyPi)](https://pypi.org/project/nrf24/)
 - [pigpio](http://abyz.me.uk/rpi/pigpio/)
 - [Raspbian](https://www.raspberrypi.org/)
