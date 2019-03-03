// Example 2 - Receive with an end-marker
#include <Servo.h>
char incomingByte = 0; 
int positionTarget = 0;  
boolean newData = false;
Servo finger;
int inPin=7;
int servo_position=0;
int val=0;



void setup() {
  finger.attach(9);
  pinMode(inPin, INPUT);
    Serial.begin(9600);
    Serial.println("<Arduino is ready>");
}

void loop() {

    if (Serial.available() > 0) {
      incomingByte = Serial.read();
      Serial.println(incomingByte);
      Serial.println(Serial.available());   
      if (incomingByte == 'A') {
        positionTarget = 90;
        Serial.println("Successful A");   
      }
      else if (incomingByte == 'B') {
        positionTarget = 0; 
      }
    }
   
    Serial.println(positionTarget); 
    finger.write(positionTarget);


}
