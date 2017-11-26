#!/usr/bin/env python3

import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("presence")
    client.subscribe("set_playlist")

def on_message(client, userdata, msg):
    if msg.topic == "presence":
        payload = msg.payload.split(",")
        client.publish("get_playlist/"+payload[1], payload[0])
        print("Requested playlist for "+payload[0]+" as type "+payload[1])
    elif msg.topic == "set_playlist":
        print("Add song: "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()
