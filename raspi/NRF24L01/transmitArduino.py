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
CONFIG_FILE = "../config/config.ini"

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



GPIO.setmode(GPIO.BCM)

pipe = [0x31, 0x53, 0x4E, 0x53, 0x52]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 17)

radio.setPayloadSize(6)
radio.setChannel(0x76)
radio.setDataRate(NRF.BR_1MBPS)
radio.setPALevel(NRF24.PA_MIN)

radio.setAutoAck(True)
radio.enableDynamicPayload()
radio.enableAckPayload()

radio.openWritingPipe(pipe)
radio.printDetails()
radio.show_registers()

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
    rgb_ch1 = rgb_data[0:3]
    rgb_ch2 = rgb_data[3:6]

    # Try sending data using radio
    try:
        payload = struct.pack(
            "<BBBBBB",
            rgb_ch1[0],
            rgb_ch1[1],
            rgb_ch1[2],
            rgb_ch2[0],
            rgb_ch2[1],
            rgb_ch2[2]
        )

        radio.reset_packages_lost()
        radio.send(payload)
        print(payload)
        logging.debug("Payload: " + str(payload))
    except:
        traceback.print_exc()
        radio.power_down()

# optional: if you want to use multicast use this function with the universe as parameter
receiver.join_multicast(int(UNIVERSE_ID))
