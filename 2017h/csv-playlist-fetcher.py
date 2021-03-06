#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import csv

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("get_playlist/csv")

def on_message(client, userdata, msg):
    print("Received playlist request for user "+msg.payload)
    playlist_list = ""+msg.payload+"\n"
    try:
        with open(msg.payload+".csv") as playlist_file:
            playlist = csv.reader(playlist_file, delimiter=',', quotechar='"')
            for song in playlist:
                playlist_list = playlist_list+"\n\""+song[0]+"\",\""+song[1]+"\""
            client.publish("set_playlist", playlist_list)
    except:
        print("An error occured")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()
