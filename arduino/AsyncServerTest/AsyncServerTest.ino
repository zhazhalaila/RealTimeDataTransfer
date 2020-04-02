#include <WiFi.h>
#include <WiFiAP.h>
#include <SPIFFS.h>
#include <ESPAsyncWebServer.h>
#include <MQTT.h>
#include "AsyncJson.h"
#include "ArduinoJson.h"
#include "DHT.h"

#define DHTPIN 4
#define DHTTYPE DHT11
#define LOCK 1
#define UNLOCK 0

String connect_ssid;
String connect_password;
String connect_mqtt_topic;
String connect_mqtt_suscribe_topic;

int sendStatus = UNLOCK;

float humidity;
float temperature;

unsigned long lastMillis = 0;
unsigned long lastSensorMillis = 0;

DHT dht(DHTPIN, DHTTYPE);
WiFiClient net;
MQTTClient client;

AsyncWebServer server(80);

//mqtt connect
void connect() {
  Serial.print("connecting...");
  String clientId = "My" + connect_mqtt_topic;
  while (!client.connect((const char*)clientId.c_str(), "try", "try")) {
    Serial.print(".");
  }

  Serial.println("\nconnected!");
}

void messagePublish() {
  Serial.println("connect successfully");
  //create json object to store data
  DynamicJsonBuffer jsonBuffer;
  JsonObject &monitor_value = jsonBuffer.createObject();
  monitor_value["temperature"] = String(temperature);
  monitor_value["humidity"] = String(humidity) + "%";
  String payload;
  monitor_value.printTo(payload);
  Serial.println(payload.c_str());
  //convert string type to const char[] type which mqtt client publish use
  client.publish((const char*)connect_mqtt_topic.c_str(), payload.c_str());
}

void messageReceived(String &topic, String &payload) {
  if (payload == "USER_ONLINE") {
    messagePublish();
  }
}


void setup(){
  Serial.begin(115200);
  dht.begin();
 
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

  server.on("/getWiFiStatus", HTTP_GET, [](AsyncWebServerRequest *request){
    if (WiFi.status() != WL_CONNECTED)
    {
      request->send(200, "text/plain", "{'WiFi_Connect_Status': 'Unconnected'}");
    }
    else
    {
      request->send(200, "text/plain", "{'WiFi_Connect_Status': 'Connected'}");
    }
  });

  server.on("/getMqttStatus", HTTP_GET, [](AsyncWebServerRequest *request){
    if (client.connected())
    {
      request->send(200, "text/plain", "{'MQTT_Connect_Status': 'Connected'}");
    }
    else
    {
      request->send(200, "text/plain", "{'MQTT_Connect_Status': 'Unconnected'}");
    }
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
      }
      if (root.containsKey("connect_mqtt_topic")) {
        connect_mqtt_topic = root["connect_mqtt_topic"].asString();
        connect_mqtt_suscribe_topic = "/test" + connect_mqtt_topic;
        //subscribe a topic
        client.subscribe((const char*)connect_mqtt_suscribe_topic.c_str());
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

  //check mqtt client connect status and user input
  if (!client.connected() && (connect_mqtt_topic.length() != 0))
  {
    connect();
  }

  if (millis() - lastSensorMillis > 2000 && client.connected())
  {
    humidity = dht.readHumidity();
    temperature = dht.readTemperature();
    if ((humidity > 80.0 || temperature > 40.0) && sendStatus == UNLOCK)
    {
      messagePublish();
      //after publish status is lock
      sendStatus = LOCK;
    }
    if (sendStatus == LOCK)
      Serial.println("Yeah. I'm LOCL!");
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.print("%");
    Serial.print("Tempeture: ");
    Serial.print(temperature);
    Serial.println("°C");
    lastSensorMillis = millis();
  }
  
  //send message every hour
  if (millis() - lastMillis > 3600000 && client.connected() && (connect_mqtt_topic.length() != 0) && !isnan(humidity) && !isnan(temperature))
  {
    lastMillis = millis();
    messagePublish();
    //after publish status is unlock
    if (sendStatus == LOCK)
    {
      sendStatus = UNLOCK; 
    }
  }
}
