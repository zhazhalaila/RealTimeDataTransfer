#include <WiFi.h>
#include <WiFiAP.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <SPIFFS.h>
#include <ESPAsyncWebServer.h>
#include <MQTT.h>
#include "AsyncJson.h"
#include "ArduinoJson.h"

String connect_ssid;
String connect_password;
String connect_mqtt_topic;

unsigned long lastMillis = 0;

WiFiClient net;
MQTTClient client;
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP);

AsyncWebServer server(80);

//mqtt connect
void connect() {
  Serial.print("connecting...");
  while (!client.connect("MyEsp32Test", "try", "try")) {
    Serial.print(".");
  }

  Serial.println("\nconnected!");

  client.subscribe("/example");
}

void messageReceived(String &topic, String &payload) {
  Serial.println("incoming: " + topic + " - " + payload);
}


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

  server.on("/src/jquery-3.4.1.min.js", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(SPIFFS, "/src/jquery-3.4.1.min.js", "text/javascript");
  });
  
  //get config of wifi and mqtt server return json object
  server.on("/getConfig", HTTP_GET, [](AsyncWebServerRequest *request) {
    AsyncResponseStream *response = request->beginResponseStream("application/json");
    DynamicJsonBuffer jsonBuffer;
    JsonObject &result = jsonBuffer.createObject();
    result["connect_ssid"] = connect_ssid;
    result["connect_password"] = connect_password;
    result["connect_mqtt_topic"] = connect_mqtt_topic;
    result.printTo(*response);
    request->send(response);
  });
  
  //post config by jsonn object
  server.on("/postConfig", HTTP_POST, [](AsyncWebServerRequest *request){
      //nothing and dont remove it
  }, NULL, [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total){
    AsyncResponseStream *response = request->beginResponseStream("application/json");
    DynamicJsonBuffer jsonBuffer;
    JsonObject& root = jsonBuffer.parseObject((const char*)data);
    if (root.success()) 
    {
      if (root.containsKey("connect_ssid") && root.containsKey("connect_password")) {
        connect_ssid = root["connect_ssid"].asString();
        connect_password = root["connect_password"].asString();
        //convert string type to const char* type which wifi.begin use
        WiFi.begin((const char*)connect_ssid.c_str(), (const char*)connect_password.c_str());
        client.begin("broker.hivemq.com", net);
        client.onMessage(messageReceived);
        connect();
        timeClient.begin();
      }
      if (root.containsKey("connect_mqtt_topic")) {
        connect_mqtt_topic = root["connect_mqtt_topic"].asString();
      }
      root.printTo(*response);
      request->send(response);
    } 
    else 
    {
      request->send(404, "text/plain", "Sorry, this is an error!");
    }
  });
  
  server.begin();
}
 
void loop()
{
  client.loop();

  //check mqtt client connect status
  if (!client.connected() && (connect_mqtt_topic.length() != 0))
  {
    connect();
  }

  //send message every ten seconds
  if (millis() - lastMillis > 10000 && client.connected() && (connect_mqtt_topic.length() != 0))
  {
    Serial.println("connect successfully");
    //update date
    timeClient.update();
    //create json object to store data
    DynamicJsonBuffer jsonBuffer;
    JsonObject &monitor_value = jsonBuffer.createObject();
    monitor_value["temperature"] = "28.5";
    monitor_value["humidity"] = "19%";
    monitor_value["time"] = timeClient.getFormattedDate();
    String payload;
    monitor_value.printTo(payload);
    Serial.println(payload.c_str());
    lastMillis = millis();
    //convert string type to const char[] type which mqtt client publish use
    client.publish((const char*)connect_mqtt_topic.c_str(), payload.c_str());
  }
}
