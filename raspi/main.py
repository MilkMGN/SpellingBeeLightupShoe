import sacn
# import circuitpython-nrf24l01
import time
import os
import configparser
import platform
import codecs

# Import config file
CONFIG_FILE = "./config/config.ini"

config = configparser.ConfigParser()
config.read_file(codecs.open(CONFIG_FILE, "r", "utf-8"))

# set clear type
platype = platform.system()
if platype == "Linux":
    clear = lambda: os.system('clear')
elif platype == "Windows":
    clear = lambda: os.system('cls')

# Set settings based off of config file
UNIVERSE_ID=config.get("sACN", "universe")

# provide an IP-Address to bind to if you are using Windows and want to use multicast
receiver = sacn.sACNreceiver()
receiver.start()  # start the receiving thread

# define a callback function
@receiver.listen_on('universe', universe=UNIVERSE_ID)  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
    clear()
    print(packet.dmxData)  # print the received DMX data

# optional: if you want to use multicast use this function with the universe as parameter
receiver.join_multicast(1)


time.sleep(10)  # receive for 10 seconds
receiver.stop()
