import sacn
import nrf24
import pigpio
import time
import os
import configparser
import codecs
import platform
import struct
import logging
import pytz
from datetime import datetime, timedelta

# Import config file
CONFIG_FILE = "./config/config.ini"

config = configparser.ConfigParser()
config.read_file(codecs.open(CONFIG_FILE, "r", "utf-8"))

# Set settings based off of config file
# Get sACN universe
UNIVERSE_ID=config.get("sACN", "universe")

# Grab channels to be used for the shoe RGB values, and take one as Python counts from 0, not 1.
SHOE_CH1=int(config.get("Shoes", "shoe_one_channel")) - 1
SHOE_CH2=int(config.get("Shoes", "shoe_two_channel")) - 1
# Configure nrf24 variables, a lot of these are not use and so are hashed out
RADIO_HOSTNAME = config.get("Radio", "hostname")
RADIO_PORT = config.get("Radio", "port")
RADIO_ADDRESS = config.get("Radio", "address")
# RADIO_GPIO_MOSI = config.get("Radio", "gpio_mosi")
# RADIO_GPIO_MISO = config.get("Radio", "gpio_miso")
# RADIO_GPIO_SCK = config.get("Radio", "gpio_sck")
RADIO_GPIO_CE = int(config.get("Radio", "gpio_ce"))
# RADIO_GPIO_CSN = config.get("Radio", "gpio_csn")

# i have spent too much time on a stupid debug component ^MilkMGN
#  Get timezone
TIMEZONE_CFG = config.get("Logging", "timezone")
