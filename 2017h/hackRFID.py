#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import datetime
import paho.mqtt.client as mqtt
import os

mqttpub = mqtt.Client()
global activated, tDiffSec
activated = datetime.datetime.now()

def mqttPublish(topic, payload):

    global activated, tDiffSec
    publishTime = datetime.datetime.now()
    timeDiff = publishTime - activated
    print (timeDiff)
    tDiffSec = (timeDiff.microseconds * 0.000001) + timeDiff.seconds
    print (tDiffSec)
    if tDiffSec >= 15.0:
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
        tDiffSec = 0

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    continue_reading = False
    rfid_access.close() # cursor for close()
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
#    if status == MIFAREReader.MI_OK:
#        print ("--------------------------")
#        print ("Card detected")
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()
    token_id = str(uid[0:4])

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        hexUid=""
        for val in uid[0:4]:
            hexUid = hexUid+"{:02x}".format(val)
        # Print UID
#        print "Card read: UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
#        print "         (hex}:"+str(hexUid)
        mqttPublish('auth/door1',hexUid)
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 0, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
#            print MIFAREReader.MFRC522_Read(0)
            MIFAREReader.MFRC522_StopCrypto1()
        else:
            print ("Authentication error")

    time.sleep(0.01)
