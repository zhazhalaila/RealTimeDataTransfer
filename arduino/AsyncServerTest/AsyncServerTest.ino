#include "WiFi.h"
#include "WiFiAP.h"
#include "SPIFFS.h"
#include "ESPAsyncWebServer.h"

String connect_ssid;
String connect_password;

AsyncWebServer server(80);
 
void setup(){
  Serial.begin(115200);
 
  if(!SPIFFS.begin()){
     Serial.println("An Error has occurred while mounting SPIFFS");
     return;
  }

  //run ap and station at the same time
  WiFi.mode(WIFI_AP_STA);

  Serial.print("Setting soft-AP ... ");
  Serial.println(WiFi.softAP("esp32", "66666666") ? "Ready" : "Failed!");

  Serial.print("Soft-AP IP address = ");
  Serial.println(WiFi.softAPIP());
 
  server.on("/index", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(SPIFFS, "/index.html", "text/html");
  });
 
  server.on("/src/bootstrap.min.css", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(SPIFFS, "/src/bootstrap.min.css", "text/css");
  });

  server.on("/FormSubmit", HTTP_POST, [](AsyncWebServerRequest *request) {
    Serial.println("submit hit.");
    int params = request->params();
    Serial.printf("%d params sent in\n", params);
    // get params
    for (int i = 0; i < params; i++)
    {
      AsyncWebParameter *p = request->getParam(i);
      if (p->isPost())
      {
        Serial.printf("_POST[%s]: %s", p->name().c_str(), p->value().c_str());
      }
      else
      {
        Serial.printf("_GET[%s]: %s", p->name().c_str(), p->value().c_str());
      }
    }
    //get params value
    if (request->hasParam("connect_ssid", true) && request->hasParam("connect_password", true))
    {
      connect_ssid = request->getParam("connect_ssid", true)->value();
      connect_password = request->getParam("connect_password", true)->value();
      //convert string type to char* type as parameters which wifi.begin use
      WiFi.begin((const char*)connect_ssid.c_str(), (const char*)connect_password.c_str());
    }
    else
    {
      connect_ssid = "not specified";
      connect_password = "not specified";
    }
    request->send(200, "text/plain", "Submit: " + connect_ssid + connect_password);
    Serial.print("Ssid: ");
    Serial.println(connect_ssid);
    Serial.print("Password: ");
    Serial.println(connect_password);
  });
  server.begin();
}
 
void loop(){}