// This #include statement was automatically added by the Particle IDE.
#include "MQTT.h"

int pumpControl(String size);

void callback(char* topic, byte* payload, unsigned int length);

MQTT client("broker.emqx.io", 1883, callback);

// recieve message
void callback(char* topic, byte* payload, unsigned int length) {
    char p[length + 1];
    memcpy(p, payload, length);
    p[length] = NULL;
}

void setup() {
    // connect to the server(unique id by Time.now())
    client.connect("sparkclient_" + String(Time.now()));
    
    // publish/subscribe
    if (client.isConnected()) {
        client.subscribe("pub/pump-1");
    }
    
    // register the cloud function
    Particle.function("pumpAccess", pumpControl);
}

void loop() {
    if (client.isConnected())
    {
        client.loop();
    }
}

int pumpControl(String size) {
    if(strcmp(size, "s") == 0)
    {
        client.publish("pub/pump-1","s");
        return 0;
    }
    else if(strcmp(size, "m") == 0)
    {
        client.publish("pub/pump-1","m");
        return 0;
    }
    else if(strcmp(size, "l") == 0)
    {
        client.publish("pub/pump-1","l");
        return 0;
    }
    else
    {
        return -1;
    }
}