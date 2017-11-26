#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import pafy
import time
from omxplayer.player import OMXPlayer
import requests

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("set_song")

def on_message(client, userdata, msg):
    try:
        print("Received song request: "+msg.payload)
        r = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q="+msg.payload+"&key=AIzaSyCudOMcwOsl-EGRHCyK5tWgwY6tWWsYs1o")
        video_id = r.json()
        video = pafy.new(str(video_id['items'][0]['id']['videoId']))
        bestaudio = video.getbestaudio()
        print("Starting player")
        player = OMXPlayer(bestaudio.url)
        print("Playing now!")
        time.sleep(15)
        player.quit()
        print("Song Finished")
    except:
        print("An error occured")
    client.publish("get_song", "New song please!")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()
