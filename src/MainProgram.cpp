#include "MainProgram.hpp"

// --------Initialised at global scope----------
SemaphoreHandle_t clientMutex;
bool ledState = LOW;
unsigned long now = millis();
unsigned long lastTrigger = 0;
unsigned long lastBlink = 0;
unsigned long blinkNow = millis();
boolean motionDetectedFlag = false;
boolean startTimer = false;
unsigned long lastTimeBotRan = 0;
WiFiClientSecure client;

// --------------------------

void setup() {
  Serial.begin(115200);
  Serial.println("Initializing sensors...");
  dht.begin();
  delay(2000);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  pinMode(BuzzerPin, OUTPUT);
  digitalWrite(BuzzerPin, LOW);
  bool response = ConnectToWifi();
  server.on("/", handleRoot);
  server.on("/readings", handleReadings);
  server.on("/led_on", handleLedOn);
  server.on("/led_off", handleLedOff);
  server.begin();
  Serial.println("🌐 Web server started! Open this IP in your browser.");

  #ifdef TELEGRAM_CERTIFICATE_ROOT
  client.setCACert(TELEGRAM_CERTIFICATE_ROOT);
  #else
  client.setInsecure();
  #endif
  Serial.println("Testing Telegram connection...");
  bool sent = bot.sendMessage(CHAT_ID, "🚀 ESP32 is online and ready!", "");
  Serial.println(sent ? "Message sent OK" : "Message failed");
  Serial.println("Allowing MQ-135 to warm up for 20 seconds...");
  delay(20000);
  Serial.println("MQ-135 warm-up complete.");
  Serial.print("Atmospheric standard:");
  Serial.println(ATMOCO2);
  // Serial.begin( 115200 ); // Serial port for debugging purposes
  pinMode( PIRSensor, INPUT_PULLUP); // PIR Motion Sensor mode INPUT_PULLUP
  pinMode( led, OUTPUT );
  digitalWrite( led, LOW );
  // Set PIRSensor pin as interrupt, assign interrupt function and set RISING mode
  attachInterrupt( digitalPinToInterrupt(PIRSensor), detectsMovement, RISING); 
  // sensors.begin();
  Serial.println("Setup complete");
  clientMutex = xSemaphoreCreateMutex();
  xTaskCreate(TakeAtmosphericReadingsTask,"ReadAirQuantitiesTask" ,10240,NULL,1,NULL);
  xTaskCreate(PresenceSensorTask,"SensePresenceTask" ,10240,NULL,1,NULL);
}


// -------------------
// Presense Sensing Task
void TakeAtmosphericReadingsTask(void *){
  while (1)
  {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(2000);
    server.handleClient();
    
    if (millis() - lastTimeBotRan > BOT_MTBS) {
      int numNewMessages = bot.getUpdates(bot.last_message_received + 1);
      while (numNewMessages) {
        handleNewMessages(numNewMessages);
        numNewMessages = bot.getUpdates(bot.last_message_received + 1);
      }
      lastTimeBotRan = millis();
    }
    
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
    
    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("❌ Failed to read from DHT11. Check wiring or add pull-up resistor.");
    } else {
      Serial.print("🌡️ Temperature: ");
      Serial.print(temperature);
      Serial.print(" °C  |  💧 Humidity: ");
      Serial.print(humidity);
      Serial.println(" %");
    }
    
      int analogValue = analogRead(MQ135_PIN);
      // float voltage = analogValue * (3.3 / 4095.0);
      float voltage = (analogValue/ 4095.0) * 3.3;
      float actualVoltage = voltage * VOLTAGE_DIVIDER_RATIO;
      float ppm = gasSensor.getPPM();
      float RS = RLOAD *((5.0 / actualVoltage) - 1);
      float RS_R0 = RS / RZERO;
      String AirStatus;
      bool LEDValue;
      bool BUZZERValue;
      float CorrectedPPM = gasSensor.getCorrectedPPM(temperature, humidity);
    
      if (RS_R0 < 0.05) RS_R0 = 0.05;
      if (RS_R0 > 20) RS_R0 = 20;
      Serial.println("This is the ppm of CO2:");
      Serial.println({ppm});
      Serial.println("This is the corrected ppm of CO2:");
      Serial.println({CorrectedPPM});
      Serial.println("This is the rs:");
      Serial.println(RS);
      Serial.println("This is the rs_ro:");
      Serial.println(RS_R0);
    
    Serial.print("Raw analog value: ");
    Serial.print(analogValue);
    Serial.print("  |  Voltage: ");
    Serial.print(voltage);
    Serial.println(" V");
    Serial.print("  | Actual Voltage: ");
    Serial.print(actualVoltage);
    Serial.println(" V");
    
    if (ppm > 8000 || RS < 7 || RS_R0 < 0.15)
    {
        AirStatus = "Hazardous";
        LEDValue = true;
        BUZZERValue = true;
        Serial.print("💨 Air Quality:");
        Serial.println({AirStatus});
        Controller(ledPin, LEDValue);
        Controller(BuzzerPin, BUZZERValue);
      }
      else if (ppm > 4000 || RS < 9 || RS_R0 < 0.2)
      {
          AirStatus = "Very Poor";
          LEDValue = true;
          BUZZERValue = true;
          Serial.print("💨 Air Quality:");
          Serial.println({AirStatus});
          Controller(ledPin, LEDValue);
          Controller(BuzzerPin, BUZZERValue);
      }
      else if (ppm > 2000 || RS < 10 || RS_R0 < 0.3)
      {
          AirStatus = "Poor";
          LEDValue = true;
          BUZZERValue = true;
          Serial.print("💨 Air Quality:");
          Serial.println({AirStatus});
          Controller(ledPin, LEDValue);
          Controller(BuzzerPin, BUZZERValue);
      }
      else if (ppm > 1000 || RS < 15 || RS_R0 < 0.6){
          AirStatus = "Bad";
          LEDValue = true; //blinking
          BUZZERValue = false;
          Serial.print("💨 Air Quality:");
          Serial.println({AirStatus});
          Controller(ledPin, LEDValue);
          Controller(BuzzerPin, BUZZERValue);
      }
      else if (ppm > 750 || RS < 17 || RS_R0 < 0.49){
          AirStatus = "Moderate";
          LEDValue = false; 
          BUZZERValue = false;
          Serial.print("💨 Air Quality:");
          Serial.println({AirStatus});
          Controller(ledPin, LEDValue);
          Controller(BuzzerPin, BUZZERValue);
      }
      else
      {
          AirStatus = "Good";
          LEDValue = false;
          BUZZERValue = false;
          Serial.print("💨 Air Quality:");
          Serial.println({AirStatus});
          digitalWrite(ledPin, LOW);
          Controller(ledPin, LEDValue);
          Controller(BuzzerPin, BUZZERValue);
      }
    Serial.println("--------------------------\n");
    vTaskDelayUntil(&xLastWakeTime, xFrequency); 
  }  
}

// -------------------


//------------Presense sensing Task----------
void PresenceSensorTask(void *){
  while(1){
    // Serial.println(digitalRead(PIRSensor));
    // vTaskDelay(1000);
    if (motionDetectedFlag && !startTimer)
    {
      motionDetectedFlag = false;
      Serial.println( " MOTION DETECTED " );
      Serial.println("Turning ON the LED");
      startTimer = true;
      lastTrigger = millis();
    }
    if (startTimer && ((millis() - lastBlink) > timeSeconds))
    {
    int pinState = digitalRead(led);
    if (pinState == 0)
    {
        blinkLedOn();
    } 
    else
    {
      blinkLedOff();
    }
    }
    now = millis();
    if( startTimer && (now - lastTrigger > ( timeSeconds*50)))
    {
      Serial.println("===========================");
      Serial.println("In here now");
      Serial.println(" Turning OFF the LED " );
      digitalWrite( led, LOW );
      startTimer = false;
    }

  }
}
//------------Presense sensing Task----------
void loop() {
  // Empty loop function
}
