#!/usr/bin/python3 
import paho.mqtt.client as mqtt
import time

from gpiozero import LED

led26 = LED(26)
led19 = LED(19)
led13 = LED(13)
led16 = LED(16)
led20 = LED(20)
led21 = LED(21)


def on_connect(mqttsub, obj, flags, rc):
    print("rc: " + str(rc))

def on_message(mqttsub, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + msg.payload.decode('UTF-8'))
    topic, door_num = msg.topic.split('/')
    x, uuid = msg.payload.decode('UTF-8').split(':')
    print (door_num, uuid)

    conn = my.connect(user='ben', password='hackathon', host='192.168.113.249', database='hack')
    cursor1 = conn.cursor()
    sel1 = ("SELECT last_seen, name FROM rfid_access WHERE uuid = '{}';".format(uuid))
    cursor1.execute(sel1)
    for (last_seen, name) in cursor1:
        #print (uuid)
        ret_val = (last_seen, name)
    
    last_seen, name = ret_val
    print (last_seen.strftime('%d %b, %H:%M'))
    print (name)

    lcd_string(str(name), LCD_LINE_1)
    lcd_string(str(last_seen.strftime('%d %b, %H:%M')), LCD_LINE_2)
    time.sleep(3)


def on_publish(mqttsub, obj, mid):
    #print("mid: " + str(mid))
    pass

def on_subscribe(mqttsub, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

mqttsub = mqtt.Client()
mqttsub.on_message = on_message
mqttsub.on_connect = on_connect
mqttsub.on_publish = on_publish
mqttsub.on_subscribe = on_subscribe
mqttsub.connect("192.168.113.249", 1883, 60)
mqttsub.subscribe("doors/#", 0)

mqttsub.loop_forever()
