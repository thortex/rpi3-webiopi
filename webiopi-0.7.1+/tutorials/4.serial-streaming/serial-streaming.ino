int analogValue = 0;
int i;

void setup() {
  // open the serial port at 9600 bps:
  Serial.begin(9600);
}

void loop() {
  // read the analog input on all pins :
  for (i = 0; i<=5; i++) {
    analogValue = analogRead(i);

    // print it on serial
    Serial.print(i);
    Serial.print("=");
    Serial.println(analogValue);
  }
  
  // delay 1 second before the next reading:
  delay(1000);
}

