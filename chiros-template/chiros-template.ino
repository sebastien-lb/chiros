#include <ArduinoJson.h>

#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <ESPmDNS.h>

const char* ssid = "{VIA}";
const char* password = "connexion";

WebServer server(80);

/////////
// utils

JsonObject& extractPostedPayload(){
  
  StaticJsonBuffer<2000> jsonBuffer;
  
  // reset JsonObject
  JsonObject& root = jsonBuffer.parseObject("");
  
  if(server.hasArg("plain")){
    JsonObject& root = jsonBuffer.parseObject(server.arg("plain"));
    return root;
  }else{
    return root;
  }
}

/////////
// routesHandler

void handleRegister() {
  JsonObject& registerPayload = extractPostedPayload();
  if(registerPayload.size()==0){
    return handleErrorNoPayload();
  }
  const char* action_id = registerPayload["action_id"];
  Serial.println(action_id);
  server.send(200, "text/plain", "great, you have been registered :)");
}

void handleErrorNoPayload(){
  server.send(401, "text/plain", "Error, no payload found in the request.");
}

void handleRoot() {
  server.send(200, "text/plain", "/register is available");
}

void handleNotFound() {
  String message = "Url Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
}

/////////
// init

void initWifi(){
  Serial.println("Initializing wifi connection with:");
  Serial.print("SSID: ");Serial.println(ssid);
  Serial.print("Password: ");Serial.println(password);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected with ip adress: ");Serial.println(WiFi.localIP());
}

void initRouting(){
  server.on("/", handleRoot);
  
  server.on("/register", handleRegister);

  server.on("/inline", []() {
    server.send(200, "text/plain", "this works as well");
  });
}

/////////
// SETUP

void setup(void) {
  Serial.begin(115200);

  // conntect to the wifi network as
  // specified on top of the program
  initWifi();

  if (MDNS.begin("esp32")) {
    Serial.println("MDNS responder started");
  }

  // define all routes callable
  initRouting();

  // raise an error if another route is called
  server.onNotFound(handleNotFound);

  server.begin();
  Serial.println("HTTP server started");
}

/////////
// LOOP

void loop(void) {
  server.handleClient();
}
