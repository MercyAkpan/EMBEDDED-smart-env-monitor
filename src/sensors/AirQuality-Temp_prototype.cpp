// // Controlling ESP32 with Telegram + DHT11 + MQ135 Sensor + Web Dashboard

#include "AirQuality-Temp_prototype.hpp"
// #include "WiFi-c.h"

DHT dht(DHTPIN, DHTTYPE);
MQ135 gasSensor = MQ135(MQ135_PIN);
WebServer server(80);

// Handle New Telegram Messages
void handleNewMessages(int numNewMessages) {
  for (int i = 0; i < numNewMessages; i++) {
    String chat_id = String(bot.messages[i].chat_id);

    if (chat_id != CHAT_ID) {
      bot.sendMessage(chat_id, "❌ Unauthorized user", "");
      continue;
    }

    String text = bot.messages[i].text;

    if (text == "/start") {
      String welcome = "👋 Welcome to ESP32 Telegram Bot!\n\n";
      welcome += "/led_on - Turn LED ON\n";
      welcome += "/led_off - Turn LED OFF\n";
      welcome += "/state - Get LED state\n";
      welcome += "/readings - Get DHT11 & MQ135 values\n";
      bot.sendMessage(chat_id, welcome, "");
    }

    if (text == "/led_on") {
      digitalWrite(ledPin, HIGH);
      ledState = HIGH;
      bot.sendMessage(chat_id, "💡 LED is now ON", "");
      Serial.println("LED is now ON");
    }

    if (text == "/led_off") {
      digitalWrite(ledPin, LOW);
      ledState = LOW;
      bot.sendMessage(chat_id, "💤 LED is now OFF", "");
      Serial.println("LED is now OFF");
    }

    if (text == "/state") {
      bot.sendMessage(chat_id, ledState ? "LED is ON" : "LED is OFF", "");
    }

    if (text == "/readings") {
      float humidity = dht.readHumidity();
      float temperature = dht.readTemperature();
      int analogValue = analogRead(MQ135_PIN);
      float voltage = analogValue * (3.3 / 4095.0);

      String airQuality;
      if (analogValue < 1000) airQuality = "💨 Clean";
      else if (analogValue < 2000) airQuality = "🌫️ Moderate";
      else if (analogValue < 3000) airQuality = "⚠️ Poor";
      else airQuality = "🚨 Very Poor";

      String message = "🌡️ Temp: " + String(temperature) + " °C\n";
      message += "💧 Humidity: " + String(humidity) + " %\n";
      message += "📟 MQ135: " + String(analogValue) + " (" + String(voltage, 2) + " V)\n";
      message += "🧭 Air Quality: " + airQuality;
      bot.sendMessage(chat_id, message, "");
    }
  }
}



// Web Server Handlers
void handleRoot() {
  String html = R"====(
<!DOCTYPE html>
<html>
<head>
<title>ESP32 Dashboard</title>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<style>
body { font-family: Arial; text-align: center; background: #f3f3f3; margin: 0; padding: 0; }
h1 { background: #333; color: white; padding: 15px; margin: 0; }
.card { background: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.2); margin: 20px; padding: 20px; }
.button { display:inline-block; padding:10px 20px; margin:10px; border:none; border-radius:5px; font-size:16px; cursor:pointer; }
.on { background:#28a745; color:white; }
.off { background:#dc3545; color:white; }
canvas { max-width: 100%; height: 250px; }
</style>
</head>
<body>
<h1> ESP32 Live Dashboard</h1>
<div class='card'>
  <h2> DHT11 & MQ135 Readings</h2>
  <p id='temp'>Temperature: -- °C</p>
  <p id='hum'>Humidity: -- %</p>
  <p id='mq'>MQ135: --</p>
  <p id='air'>Air Quality: --</p>
</div>
<div class='card'>
  <h2> LED Control</h2>
  <button class='button on' onclick='ledOn()'>Turn ON</button>
  <button class='button off' onclick='ledOff()'>Turn OFF</button>
  <p id='ledState'>LED State: OFF</p>
</div>
<div class='card'>
  <h2> Real-time Graph</h2>
  <canvas id='tempChart'></canvas>
  <canvas id='airChart'></canvas>
</div>
<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
<script>
let tempData = [], airData = [], labels = [];
let tempChart = new Chart(document.getElementById('tempChart'), {
  type: 'line', data: { labels: labels, datasets: [{ label: 'Temperature (°C)', data: tempData, borderColor: 'red', fill: false }] },
  options: { scales: { y: { beginAtZero: true } } }
});
let airChart = new Chart(document.getElementById('airChart'), {
  type: 'line', data: { labels: labels, datasets: [{ label: 'Air Quality (ADC)', data: airData, borderColor: 'blue', fill: false }] },
  options: { scales: { y: { beginAtZero: true } } }
});

async function fetchData() {
  const res = await fetch('/readings');
  const data = await res.json();
  document.getElementById('temp').innerText = 'Temperature: ' + data.temperature + ' °C';
  document.getElementById('hum').innerText = 'Humidity: ' + data.humidity + ' %';
  document.getElementById('mq').innerText = 'MQ135: ' + data.analogValue + ' (' + data.voltage + ' V)';
  document.getElementById('air').innerText = 'Air Quality: ' + data.airQuality;
  document.getElementById('ledState').innerText = 'LED State: ' + (data.ledState ? 'ON' : 'OFF');

  if (labels.length > 20) { labels.shift(); tempData.shift(); airData.shift(); }
  labels.push('');
  tempData.push(data.temperature);
  airData.push(data.analogValue);
  tempChart.update(); airChart.update();
}
async function ledOn(){ await fetch('/led_on'); }
async function ledOff(){ await fetch('/led_off'); }
setInterval(fetchData, 2000);
</script>
</body></html>
)====";
  server.send(200, "text/html", html);
}

void handleReadings() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  int analogValue = analogRead(MQ135_PIN);
//   float voltage = analogValue * (3.3 / 4095.0);
    float voltage = (analogValue/ 4095.0) * 3.3;
    float actualVoltage = voltage * VOLTAGE_DIVIDER_RATIO;

  String airQuality;
  if (analogValue < 1000) airQuality = "Clean";
  else if (analogValue < 2000) airQuality = "Moderate";
  else if (analogValue < 3000) airQuality = "Poor";
  else airQuality = "Very Poor";

  String json = "{";
  json += "\"temperature\":" + String(temperature) + ",";
  json += "\"humidity\":" + String(humidity) + ",";
  json += "\"analogValue\":" + String(analogValue) + ",";
  json += "\"voltage\":" + String(voltage, 2) + ",";
  json += "\"airQuality\":\"" + airQuality + "\",";
  json += "\"ledState\":" + String(ledState ? "true" : "false");
  json += "}";

  server.send(200, "application/json", json);
}

void handleLedOn() {
  digitalWrite(ledPin, HIGH);
  ledState = HIGH;
  server.send(200, "text/plain", "LED ON");
}

void handleLedOff() {
  digitalWrite(ledPin, LOW);
  ledState = LOW;
  server.send(200, "text/plain", "LED OFF");
}


void Controller(const int pin, bool value)
{
    if (value == true)
        digitalWrite(pin, HIGH);
    else
        digitalWrite(pin, LOW);
}