#include "LDR.hpp"

void LightDetect(){
    while(1){
  int iLightValue = analogRead(LDR_PIN);

  Serial.print("Light Value: ");
  Serial.println(iLightValue);

  if (iLightValue < 1000) {
    digitalWrite(LED_PIN,HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }

  delay(500);
    }
}