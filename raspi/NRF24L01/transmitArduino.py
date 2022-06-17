import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
import configparser
import codecs
import platform
import struct
import logging
import pytz
from datetime import datetime, timedelta
import sacn

# Import config file
CONFIG_FILE = "config/config.ini"

config = configparser.ConfigParser()
config.read_file(codecs.open(CONFIG_FILE, "r", "utf-8"))

# Set settings based off of config file
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
#timestamp 12:01
UNIVERSE_ID = int(config.get("sACN", "universe"))
TIMEZONE_CFG = config.get("Logging", "timezone")

GPIO.setmode(GPIO.BCM)

pipe = [0x31, 0x53, 0x4E, 0x53, 0x52]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 17)

radio.setPayloadSize(6)
radio.setChannel(0x76)
radio.setDataRate(NRF24.BR_250KBPS)
radio.setPALevel(NRF24.PA_MIN)

radio.openWritingPipe(pipe)
radio.printDetails()

receiver = sacn.sACNreceiver()
receiver.start()

@receiver.listen_on('universe', universe=int(UNIVERSE_ID))  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
    # clear()
    rgb_data = packet.dmxData[SHOE_CH1:SHOE_CH2 + 3]
    print(rgb_data, datetime.now())  # print the received DMX

    # Create a string to be used in the log
    rgb_str = ''
    for x in range(len(rgb_data)):
        rgb_str += str(rgb_data[x]) + ', '
 #
    logging.debug(f'{datetime.now(pytz.timezone(TIMEZONE_CFG))}' + rgb_str)
    # Assign the data in the appropriate channels to two tuples
    # Assign first shoes 2 zones
    rgb_ch1 = rgb_data[0:3]
    rgb_ch2 = rgb_data[3:6]

    # Assign second shoes 2 zones
    rgb_ch3 = rgb_data[7:9]
    rgb_ch4 = rgb_data[10:12]

    # Make payload
    payload = [
        rgb_data[0],
        rgb_data[1],
        rgb_data[2],
        rgb_data[3],
        rgb_data[4],
        rgb_data[5],
        rgb_data[6],
        rgb_data[7],
        rgb_data[8],
        rgb_data[9],
        rgb_data[10],
        rgb_data[11],
    ]

    radio.write(payload)
    print(f'Fucking bitches: {payload}')

    start = time.time()
    radio.startListening()
    while not radio.available(0):
        time.sleep(1/100)
        if time.time() - start > 2:
            print("Timed out.")
            break

# optional: if you want to use multicast use this function with the universe as parameter
receiver.join_multicast(int(UNIVERSE_ID))
