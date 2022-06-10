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

# Set variable of first start
StartTimestamp = datetime.now(pytz.timezone(TIMEZONE_CFG))

# init logging
fileName='./log/'+StartTimestamp.strftime("%y_%B_%a_%H%M%S")+'-ALL.log'
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename=fileName, encoding='utf-8', level=logging.DEBUG)

# set clear type
platform = platform.system()
if platform == "Linux":
    clear = lambda: os.system('clear')
elif platform == "Windows":
    clear = lambda: os.system('cls')

# Windows and Mac cannot run this script, due to the use of pigpio, kill script before pigpiod complains
if platform == "Windows":
    print("Your OS is unsupported. Please run on Raspberry Pi.")
    logging.critical("Your OS is unsupported. Please run on Raspberry Pi.")
    time.sleep(1)
    exit()

elif platform == "darwin":
    print("Your OS is unsupported. Please run on Raspberry Pi.")
    logging.critical("Your OS is unsupported. Please run on Raspberry Pi.")
    time.sleep(1)
    exit()

# Logging test
# logging.info("INFO TEST")
# logging.debug("DEBUG TEST")
# logging.warn("WARN TEST")
# logging.error("ERROR TEST")
# logging.critical("CRITICAL TEST")
# logging.warn("Timezone is: " + TIMEZONE_CFG + "Time script started should be: " + StartTimestamp + "Currently: " + str(datetime.now(tzinfo=ZoneInfo(TIMEZONE_CFG))))

def gpio_interrupt(gpio, level, tick):

    # Interrupt information.
    print(f"Interrupt: gpio={gpio}, level={['LOW', 'HIGH', 'NONE'][level]}, tick={tick}")
    logging.debug(f"Interrupt: gpio={gpio}, level={['LOW', 'HIGH', 'NONE'][level]}, tick={tick}")

    # Check result of last send operation.
    if nrf.get_packages_lost() == 0:
        print(f"Success: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
        logging.debug(f"Success: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
    else:
        print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
        logging.error(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")

    # Reset and enter RX mode.
    nrf.reset_packages_lost()
    nrf.power_up_rx()

def init_radio(hostname: str, port: int, gpio: int, address: str) -> nrf24.NRF24:
    '''Returns a NRF24 object given a valid hostname, port, gpio and address.'''
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        sys.exit()

    pi.callback(gpio, pigpio.FALLING_EDGE, gpio_interrupt)

    nrf = nrf24.NRF24(pi, ce=gpio, payload_size=nrf24.RF24_PAYLOAD.DYNAMIC, channel=100, data_rate=nrf24.RF24_DATA_RATE.RATE_250KBPS, pa_level=nrf24.RF24_PA.LOW)
    nrf.set_address_bytes(len(address))
    nrf.open_writing_pipe(address)

    nrf.show_registers()

    return nrf

print("Starting...")
logging.info("Starting...")
print("OS is " + platform)
logging.debug("OS is " + platform)
print("Universe is " + UNIVERSE_ID)
logging.debug("Universe is " + UNIVERSE_ID)
print(f'Shoe 1 channel is {str(SHOE_CH1)}')
logging.debug(f'Shoe 1 channel is {str(SHOE_CH1)}')
print(f'Shoe 2 channel is {str(SHOE_CH2)}')
logging.debug(f'Shoe 2 channel is {str(SHOE_CH2)}')
time.sleep(0.5)
print("Initialising Radio...")
logging.info("Initialising Radio...")

# provide an IP-Address to bind to if you are using Windows and want to use multicast
receiver = sacn.sACNreceiver()
receiver.start()  # start the receiving thread

# Initialise the radio and set up for sending data
nrf = init_radio(RADIO_HOSTNAME, RADIO_PORT, RADIO_GPIO_CE, RADIO_ADDRESS)

#init finishes here for some reason
time.sleep(2)
print("Done!")
logging.info("Done!")

# define a callback function
@receiver.listen_on('universe', universe=int(UNIVERSE_ID))  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
    # clear()
    print(packet.dmxData[SHOE_CH1:SHOE_CH2 + 3], datetime.now())  # print the received DMX
    logging.debug(f'{datetime.now()}: {packet.dmxData[SHOE_CH1:SHOE_CH2 + 3]}')
    # Assign the data in the appropriate channels to two tuples
    rgb_ch1 = packet.dmxData[SHOE_CH1:SHOE_CH1 + 3]
    rgb_ch2 = packet.dmxData[SHOE_CH2:SHOE_CH2 + 3]

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

        nrf.reset_packages_lost()
        nrf.send(payload)
        print(payload)
        logging.debug("Payload: ",payload)
    except:
        traceback.print_exc()
        nrf.power_down()

# optional: if you want to use multicast use this function with the universe as parameter
receiver.join_multicast(int(UNIVERSE_ID))
