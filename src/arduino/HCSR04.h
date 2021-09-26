#define TIMEOUT     100000
#define SOUND_SPEED 0.0340 // (mm / us)

class Ultrasonic {
  public:
    Ultrasonic(uint8_t burst, uint8_t echo);
    ~Ultrasonic() = default;

    float distance();
  private:
    uint8_t burst_pin;
    uint8_t echo_pin;
};

Ultrasonic::Ultrasonic(uint8_t burst, uint8_t echo)
{
  this->burst_pin = burst;
  this->echo_pin = echo;

  pinMode(burst, OUTPUT);
  pinMode(echo, INPUT);
}

float Ultrasonic::distance() {
  long timeout = 100000;

  digitalWrite(burst_pin, HIGH);
  delayMicroseconds(10);
  digitalWrite(burst_pin, LOW);

  while(--timeout && !digitalRead(echo_pin));
  long echo_delay = micros();
  
  if (!timeout) return -1;
  timeout = 100000;

  while(--timeout && digitalRead(echo_pin));
  echo_delay = micros() - echo_delay;

  float distance = (float)echo_delay * SOUND_SPEED / 2.0;
  return distance;
}
