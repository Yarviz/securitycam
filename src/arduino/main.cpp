#include "HCSR04.h"

Ultrasonic sonic(9, 10);

void setup() {
  Serial.begin(9600);
}

void loop() {
  float total = 0;
  for (int i = 0; i < 5; ++i) {
    total += sonic.distance();
    delay(200);
  }
  Serial.println(total / 5.0);
}
