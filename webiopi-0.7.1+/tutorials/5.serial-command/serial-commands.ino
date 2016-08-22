char input;

void setup() {
  // open the serial port at 9600 bps:
  Serial.begin(9600);
  pinMode(2, INPUT);
}

void loop() {
  if (Serial.available() > 0) {
    input = Serial.read();
    switch (input) {
      
      // "t" command: returns time in millis since reset/powerup
      case 't':
        Serial.println(millis());
        break;

      // "a" command: read and returns analog channel 0
      case 'a':
        Serial.println(analogRead(0));
        break;

      // "d" command: read and returns digital channel 2
      case 'd':
        Serial.println(digitalRead(2));
        break;
        
      default:
        break;
    }
  }
}

