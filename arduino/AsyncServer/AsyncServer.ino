#include "WiFi.h"
#include "ESPAsyncWebServer.h"
 
const char *ssid = "MyESP32AP";
const char *password = "testpassword";
 
AsyncWebServer server(80);
 
void setup(){
  Serial.begin(115200);

  WiFi.mode(WIFI_AP_STA);
 
  WiFi.softAP(ssid, password);
  
  Serial.println();
  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());
 
  server.on("/hello", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(200, "text/plain", "Hello World");
  });
 
  server.begin();
}
 
void loop(){}
