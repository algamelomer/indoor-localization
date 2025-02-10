#include <WiFi.h>
#include <WiFiClient.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "WE_FD1620";  // Connect to your local Wi-Fi
const char* password = "24031401";
const char* serverUrl = "http://192.168.1.202:5000/locate";  // Server IP

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
    int scanResult = WiFi.scanNetworks(false, true); // Scan hidden APs
    
    if (scanResult > 0) {
      DynamicJsonDocument scanData(1024);
      for (int i = 0; i < scanResult; ++i) {
        String ssid = WiFi.SSID(i);
        if (ssid.startsWith("ESP32_")) {  // Filter your ESP32 APs
          scanData[ssid] = WiFi.RSSI(i);  // Store SSID and RSSI
        }
      }

      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");

      String jsonPayload;
      serializeJson(scanData, jsonPayload);

      Serial.println("\nSending scan data:");
      serializeJsonPretty(scanData, Serial); // Print formatted JSON
      Serial.println();

      int httpCode = http.POST(jsonPayload);
      
      if (httpCode == HTTP_CODE_OK) {
        String response = http.getString();
        Serial.print("Predicted Location: ");
        Serial.println(response);
      } else {
        Serial.print("HTTP Error: ");
        Serial.println(httpCode);
        Serial.print("Response: ");
        Serial.println(http.getString()); // Print server response
      }
      http.end();
    } else {
      Serial.println("No networks found!");
    }
    WiFi.scanDelete();
    delay(5000); // Wait 5 seconds between scans
  }
}