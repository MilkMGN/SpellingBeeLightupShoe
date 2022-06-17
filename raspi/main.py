import sacn
import time
import os
import codecs
import struct
import logging
import pytz
from datetime import datetime, timedelta
from digitalio import DigitalInOut
import spidev
import board
from circuitpython_nrf24l01.rf24 import RF24

# Set variable of first start
TIMEZONE = 'Australia/Brisbane'
StartTimestamp = datetime.now(pytz.timezone(TIMEZONE))

# init logging
fileName='./log/'+StartTimestamp.strftime("%y_%B_%a_%H%M%S")+'-ALL.log'
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename=fileName, encoding='utf-8', level=logging.DEBUG)

SPI_BUS = spidev.SpiDev()
CSN_PIN = 0
CE_PIN = DigitalInOut(board.D22)

# Initialise the NRF24L01 using the above connections
nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)

# Radio power level set low for testing
nrf.pa_level = -12

# Need to be a byte array, address of radio
address = b"1Node"
radio_number = 0 # Transmitting radio

nrf.open_tx_pipe(address)

# Following lines are necessary with compatibility with TMRh20 library
nrf.allow_ask_no_ack = False
nrf.dynamic_payloads = False
nrf.payload_length = 12

# Set listening to false because we are only transmitting
nrf.listen = False

def transmit(data, nrf: RF24) -> None:
    '''Takes a list of 6 integers, converts them to bytes and transmits them.'''
    buffer = struct.pack(
        "<BBBBBBBBBBBB",
        data[0],
        data[1],
        data[2],
        data[3],
        data[4],
        data[5],
        data[6],
        data[7],
        data[8],
        data[9],
        data[10],
        data[11]
    )
    start_timer = time.monotonic_ns()  # start timer
    result = nrf.send(buffer)
    end_timer = time.monotonic_ns()  # end timer
    if not result:
        print("send() failed or timed out")

# provide an IP-Address to bind to if you are using Windows and want to use multicast
receiver = sacn.sACNreceiver()
receiver.start()  # start the receiving thread

# define a callback function
@receiver.listen_on('universe', universe=int(1))  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
    rgb_data = packet.dmxData[498:510]
    print(rgb_data, datetime.now())  # print the received DMX

    transmit(rgb_data, nrf)
    # Create a string to be used in the log
    rgb_str = ''
    for x in range(len(rgb_data)):
        rgb_str += str(rgb_data[x]) + ', '

    logging.debug(f'{datetime.now(pytz.timezone(TIMEZONE))}' + rgb_str)

# optional: if you want to use multicast use this function with the universe as parameter
receiver.join_multicast(1)
