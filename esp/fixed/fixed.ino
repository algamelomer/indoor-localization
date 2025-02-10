#include <WiFi.h>
// #include <ESP8266WiFi.h>

const char* ssid = "ESP32_4";  // Unique SSID for each ESP32
const char* password = "password";

void setup() {
  Serial.begin(115200);
  WiFi.softAP(ssid, password);
  Serial.println("Access Point Started");
  Serial.print("SSID: ");
  Serial.println(ssid);
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());
}

void loop() {
  // Keep the AP running
}