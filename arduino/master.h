#include <Adafruit_NeoPixel.h>
#include <nRF24L01.h>
#include <printf.h>
#include <RF24.h>
#include <RF24_config.h>

#define SHOEPIN1 6
#define NUMPIXELS1 1
#define SHOEPIN2 5
#define NUMPIXELS2 1

// Set up two sets of NeoPixels (one for each shoe)
Adafruit_NeoPixel shoe1(NUMPIXELS1, SHOEPIN1, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel shoe2(NUMPIXELS2, SHOEPIN2, NEO_GRB + NEO_KHZ800);

// Set  up the NRF24L01 radio
RF24 radio(7, 8); // CE, CSN
const byte RADIO_ADDRESS[6] = '03030'; // Abitrary 3 to 5 byte address to uniquely identify the radio

void setup() {
  // Begin serial output for troubleshooting
  Serial.begin(9600);

  // Set up the radio and start listening for data
  radio.begin();
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();

  // Begin writing to LED shoes
  shoe1.begin();
  shoe2.begin();
  shoe1.show();
  shoe2.show();
}

void loop() {
  // Read data given its available
  if (radio.available()) {
    // Data received will be 2 channels of 8 bit RGB data
    byte RGBRGB[6];
    radio.read(&RGBRGB, sizeof(RGBRGB));
    Serial.println(RGBRGB);

    CH1 = shoe1.Color(RGBRGB[0], RGBRGB[1], RGBRGB[2]);
    CH2 = shoe2.Color(RGBRGB[3], RGBRGB[4], RGBRGB[5]);

    // Show the given data across the two halves of LEDs.
    shoe1.fill(CH1);
    shoe2.fill(CH2);
    shoe1.show();
    shoe2.show();
  }
}
