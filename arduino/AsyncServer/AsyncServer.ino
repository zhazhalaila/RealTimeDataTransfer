#include "WiFi.h"
#include "ESPAsyncWebServer.h"
 
const char *ssid = "cainiaoa";
const char *password = "66666666";
const char* assid = "esp32";
const char* asecret = "12345678";

AsyncWebServer server(80);
 
void setup(){
  Serial.begin(115200);

  //ap and station open at the same time
  WiFi.mode(WIFI_AP_STA);
  
  Serial.println("Creating Accesspoint");
  WiFi.softAP(assid,asecret,7,0,5);
  Serial.print("IP address:\t");
  Serial.println(WiFi.softAPIP());

  //code for test wifi dynamic config
  server.on("/hello", HTTP_GET, [](AsyncWebServerRequest *request){
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    request->send(200, "text/plain", "Hello World");
  });
 
  server.begin();
}
 
void loop(){}