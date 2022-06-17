#include <Adafruit_NeoPixel.h>
#include <RF24.h>

#define SHOEPIN1 6
#define NUMPIXELS1 60
#define SHOEPIN2 5
#define NUMPIXELS2 60

// Set up two sets of NeoPixels (one for each shoe)
Adafruit_NeoPixel shoe1(NUMPIXELS1, SHOEPIN1, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel shoe2(NUMPIXELS2, SHOEPIN2, NEO_GRB + NEO_KHZ800);

// Set  up the NRF24L01 radio
RF24 radio(7, 8); // CE, CSN
const uint8_t RADIO_ADDRESS[6] = "1Node"; // Abitrary 3 to 5 byte address to uniquely identify the radio
uint8_t payload[12] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

void setup() {
  // Begin serial output for troubleshooting
  Serial.begin(9600);

  // Set up the radio and start listening for data
  radio.begin();
  radio.openReadingPipe(1, RADIO_ADDRESS);
  radio.setPALevel(RF24_PA_MIN);
  radio.setPayloadSize(sizeof(payload));
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
    // Data received will be 4 channels of 8 bit RGB data
    radio.read(&payload, sizeof(payload));
    Serial.println(payload[0]);

    // Create 4 colours using the 12 bytes provided
    uint32_t CH1 = shoe1.Color(payload[0], payload[1], payload[2]);
    uint32_t CH2 = shoe2.Color(payload[3], payload[4], payload[5]);
    uint32_t CH3 = shoe2.Color(payload[6], payload[7], payload[8]);
    uint32_t CH4 = shoe2.Color(payload[9], payload[10], payload[11]);

    // Set the odd/even pixels the colours provided (CH1 and CH2 for shoe1)
    for (int i = 0; i < NUMPIXELS1; i++) {
      if (i % 2) {
        shoe1.setPixelColor(i, CH1);
      } else {
        shoe1.setPixelColor(i, CH2);
      }
    }
    // Same for shoe2, CH3 and CH4
    for (int i = 0; i < NUMPIXELS2; i++) {
      if (i % 2) {
        shoe2.setPixelColor(i, CH3);
      } else {
        shoe2.setPixelColor(i, CH4);
      }
    }
    shoe1.show();
    shoe2.show();
  }
}
