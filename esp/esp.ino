#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Replace these with your network credentials
const char* ssid     = "WE_FD1620";
const char* password = "24031401";

// Replace with your server's address and port
const char* serverName = "http://192.168.1.202:5000/data";

void setup() {
  Serial.begin(115200);
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
}

void loop() {
  // Perform a WiFi scan
  int n = WiFi.scanNetworks();
  
  // Create a JSON document. Increase capacity if you scan many networks.
  StaticJsonDocument<1024> doc;
  doc["scan_count"] = n;
  JsonArray networks = doc.createNestedArray("networks");

  for (int i = 0; i < n; i++) {
    JsonObject net = networks.createNestedObject();
    net["ssid"] = WiFi.SSID(i);
    net["rssi"] = WiFi.RSSI(i);
    net["bssid"] = WiFi.BSSIDstr(i);
  }
  
  // Serialize JSON to a string
  String jsonData;
  serializeJson(doc, jsonData);

  // Send the data over HTTP POST if WiFi is connected
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonData);
    Serial.print("json data: ");
    Serial.println(jsonData);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      Serial.print("Response: ");
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }
  
  delay(200);
}
