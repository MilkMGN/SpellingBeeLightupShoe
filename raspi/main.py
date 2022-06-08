import sacn
import nrf24
import pigpio
import time
import os
import configparser
import codecs
import platform

# Import config file
CONFIG_FILE = "./config/config.ini"

config = configparser.ConfigParser()
config.read_file(codecs.open(CONFIG_FILE, "r", "utf-8"))

dmxFrame=""

# set clear type
platype = platform.system()
if platype == "Linux":
    clear = lambda: os.system('clear')
elif platype == "Windows":
    clear = lambda: os.system('cls')

# Set settings based off of config file
UNIVERSE_ID=config.get("sACN", "universe")
SHOE_ONE_CHANNEL=config.get("Shoes", "shoe_one_channel")
SHOE_TWO_CHANNEL=config.get("Shoes", "shoe_two_channel")

print("Starting...")
print("OS is " + platype)
print("Universe is " + UNIVERSE_ID)
print("Shoe 1 channel is " + SHOE_ONE_CHANNEL)
print("Shoe 2 channel is " + SHOE_TWO_CHANNEL)
print("Done!")
time.sleep(0.5)

# provide an IP-Address to bind to if you are using Windows and want to use multicast
receiver = sacn.sACNreceiver()
receiver.start()  # start the receiving thread

# define a callback function
@receiver.listen_on('universe', universe=int(UNIVERSE_ID))  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
    clear()
    #print(packet.dmxData)  # print the received DMX data
    packet.dmxData = dmxFrame
    #dmxFrame = (packet.dmxData)
    #print(*dmxFrame)

print(dmxFrame)

# optional: if you want to use multicast use this function with the universe as parameter
receiver.join_multicast(int(UNIVERSE_ID))

# Shoe 1 to be broadcast to the Arduino
# red1 =
# blue1 =
# green1 =

# Shoe 2 to be broadcast to the Arduino
# red2 =
# blue2 =
# green2 =

# stop receiving
#time.sleep(15)
#receiver.stop()
