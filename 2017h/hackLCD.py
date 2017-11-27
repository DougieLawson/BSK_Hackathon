#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import mysql.connector as my
import smbus
import time

I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On

ENABLE = 0b00000100 # Enable bit

E_PULSE = 0.0005
E_DELAY = 0.0005

bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT
#  print '{0:8b}'.format(bits_high)
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)
#  print '{0:8b}'.format(bits_low)
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  message = message.ljust(LCD_WIDTH," ")
  lcd_byte(line, LCD_CMD)
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def on_connect(mqttsub, obj, flags, rc):
    print("rc: " + str(rc))

def on_message(mqttsub, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + msg.payload.decode('UTF-8'))
    topic, door_num = msg.topic.split('/')
    x, uuid = msg.payload.decode('UTF-8').split(':')
    print (door_num, uuid)

    conn = my.connect(user='ben', password='hackathon', host='apollo.local', database='hack')
    cursor1 = conn.cursor()
    sel1 = ("SELECT last_seen, name FROM rfid_access WHERE uuid = '{}';".format(uuid))
    cursor1.execute(sel1)
    for (last_seen, name) in cursor1:
        #print (uuid)
        ret_val = (last_seen, name)
    
    last_seen, name = ret_val

    print (last_seen.strftime('%d %b, %H:%M'))
    print (name)

    lcd_init()

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
mqttsub.connect("apollo.local", 1883, 60)
mqttsub.subscribe("doors/#", 0)

mqttsub.loop_forever()
