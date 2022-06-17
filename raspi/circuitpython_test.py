import board
from digitalio import DigitalInOut
import busio
import sacn
from circuitpython_nrf24l01.rf24 import RF24
import time
import struct


print("Hello blinka!")

# Try to great a Digital input
pin = DigitalInOut(board.D4)
print("Digital IO ok!")

# Try to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print("I2C ok!")

# Try to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("SPI ok!")

try:
    import spidev

    SPI_BUS = spidev.SpiDev()
    CSN_PIN = 0
    CE_PIN = DigitalInOut(board.D22)

except ImportError:
    SPI_BUS = board.SPI()

    CE_PIN = DigitalInOut(board.D4)
    CSN_PIN = DigitalInOut(board.D5)

nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
print('Radio initialised!')

nrf.pa_level = -12

address = b"1SNSR"

radio_number = 0

nrf.open_tx_pipe(address)
nrf.channel = 69

print('Transmission ready!')

payload = bytearray(b'\x00\x00\x00\x00\x00\x00')

def master(count=5):
    nrf.listen = False

    print('Beginning loop!')
    while count:
        buffer = struct.pack(
            '<BBBBBB',
            payload[0],
            payload[1],
            payload[2],
            payload[3],
            payload[4],
            payload[5]
        )
        print('Transmitting data!')
        start_timer = time.monotonic_ns()
        result = nrf.send(buffer)
        end_timer = time.monotonic_ns()
        print('Data Transmitted!')

        if not result:
            print('It\'s dead, mate')
        else:
            print(f'It was successful, time to transmit was {(end_timer-start_timer) / 1000} us. Send {payload}')

            for x in payload:
                payload[x] += 50
        time.sleep(1)
        count -= 1

master()
print("done!")
