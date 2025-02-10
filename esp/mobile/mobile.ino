#include <WiFi.h>
#include <WiFiClient.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "WE_FD1620";  // Connect to your local Wi-Fi
const char* password = "24031401";
const char* serverUrl = "http://192.168.1.202:5000/train";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    int scanResult = WiFi.scanNetworks(false, true);
    
    if (scanResult > 0) {
      DynamicJsonDocument scanData(1024);
      for (int i = 0; i < scanResult; ++i) {
        String ssid = WiFi.SSID(i);
        if (ssid.startsWith("ESP32_")) {  // Filter by SSID
          scanData[ssid] = WiFi.RSSI(i);  // Use SSID as the key
        }
      }

      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");

      String location = "x4y4";  // Change this for each checkpoint
      DynamicJsonDocument payload(512);
      payload["location"] = location;
      payload["scan_data"] = scanData;

      String jsonPayload;
      serializeJson(payload, jsonPayload);

      int httpCode = http.POST(jsonPayload);
      
      if (httpCode == HTTP_CODE_OK) {
        String response = http.getString();
        Serial.println("Server response: " + response);
      } else {
        Serial.println("HTTP Error: " + String(httpCode));
      }
      http.end();
    }
    WiFi.scanDelete();
    delay(5000);
  }
}