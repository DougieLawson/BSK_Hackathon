#!/usr/bin/env python3

# CREATE TABLE `rfid_access` (
#   `token_id` char(4) DEFAULT NULL,
#   `date_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#   `last_seen` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
#   `uuid` char(36) DEFAULT NULL,
#   `name` varchar(40) DEFAULT NULL,
#   `alias` varchar(40) DEFAULT NULL,
#   `doors` varchar(200) DEFAULT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

import paho.mqtt.client as mqtt
import mysql.connector as my

mqttpub = mqtt.Client()

def mqttPublish(topic, payload):

    broker="192.168.113.249"
    port = 1883

    rc = mqttpub.connect(broker, port, 60)
    tries = 5
    while rc !=0:
        try:
            rc = mqttpub.reconnect()
            if rc != 0:
                rc = mqttpub.connect(broker, port, 60)
            if rc != 0:
                raise Exception('connectionError')
        except:
            tries -= 1
            mqttpub.disconnect()
            if tries == 0:
                raise Exception('connectionException')

    mqttpub.publish(topic, payload)


conn = my.connect(user='ben', password='hackathon', host='localhost', database='hack')

def dbCheckUpd(RFID, door_num):
    #print ("RFID:", RFID)
    cursor1 = conn.cursor()
    cursor2 = conn.cursor()
    cursor3 = conn.cursor()
    cursor4 = conn.cursor()
    sel1 = ("SELECT date_time, last_seen, uuid, mFormat, name, alias, doors FROM rfid_access WHERE token_id = '{}';".format(RFID))
    cursor1.execute(sel1)
    for (date_time, last_seen, uuid, mFormat, name, alias, doors) in cursor1:
        #print (uuid)
        ret_val = (date_time, last_seen, uuid, mFormat, name, alias, doors)

    rows = cursor1.rowcount
    #print (rows)
    if rows >=1:
        cursor1.close()
        cursor2 = conn.cursor()
        upd1 = ("UPDATE rfid_access SET last_seen = NOW() WHERE token_id = '{}';".format(RFID))
        cursor2.execute(upd1)
        conn.commit()
        cursor2.close()
    else:
        cursor3 = conn.cursor()
        isrt1 = ("INSERT into rfid_access (token_id, date_time, last_seen, uuid,mFormat, doors) VALUES('{}', NOW(), NOW(), UUID(), 'csv', 'no access');".format(RFID))
        cursor3.execute(isrt1)
        conn.commit()
        cursor3.close()
        cursor4.execute(sel1)
        for (date_time, last_seen, uuid, mFormat, name, alias, doors) in cursor4:
            ret_val = (date_time, last_seen, uuid, mFormat, name, alias, doors)
            #print (ret_val)
        cursor4.close()
    return ret_val

def on_connect(mqttsub, obj, flags, rc):
    #print("rc: " + str(rc))
    pass

def on_message(mqttsub, obj, msg):
    #print(msg.topic + " " + str(msg.qos) + " " + msg.payload.decode('UTF-8'))
    topic, door_num = msg.topic.split('/')
    RFID = msg.payload.decode('UTF-8')
    (date_time, last_seen, uuid, mFormat, name, alias, doors) = dbCheckUpd(RFID, door_num)
    #print ("door:", door_num, "doors:", doors, "user:", RFID, "uuid", uuid)
    mqttPublish('presence', uuid+","+mFormat)
    if (doors != None):
        print ("doors.find", doors.find(door_num))
        if (doors.find(door_num) >= 0):
            print("door active")
            mqttPublish("doors/"+door_num, "activated by:"+uuid)

def on_publish(mqttsub, obj, mid):
    #print("mid: " + str(mid))
    pass

def on_subscribe(mqttsub, obj, mid, granted_qos):
    #print("Subscribed: " + str(mid) + " " + str(granted_qos)
    pass

mqttsub = mqtt.Client()
mqttsub.on_message = on_message
mqttsub.on_connect = on_connect
mqttsub.on_publish = on_publish
mqttsub.on_subscribe = on_subscribe
mqttsub.connect("192.168.113.249", 1883, 60)
mqttsub.subscribe("auth/#", 0)

mqttsub.loop_forever()
