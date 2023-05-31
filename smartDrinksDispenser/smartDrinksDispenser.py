import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

# MQTT implemented - two soc's communicating
# can control the water pump
# ultrasonic sensor readings feeded to the website - not yet
# pressure sensor readings feeded to the website - not yet

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# water pump
pin = 21

# ultrasonic sensor
#LED = 18
TRIG = 23
ECHO = 24

# ultrasonic sensor 2
TRIG2 = 17
ECHO2 = 27

# led indicators
red = 6
blue = 13
green = 19
yellow = 26

GPIO.setup(yellow, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(green, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(blue, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(red, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(TRIG2,GPIO.OUT)
GPIO.setup(ECHO2,GPIO.IN)
GPIO.setup(pin,GPIO.OUT)

GPIO.output(pin, True)
GPIO.output(yellow, GPIO.LOW)
GPIO.output(green, GPIO.LOW)
GPIO.output(blue, GPIO.LOW)
GPIO.output(red, GPIO.LOW)

refreshTime = 0.2 #0.25

def turnOn(delay):
    GPIO.output(pin, False)
    print("pump on for "+str(delay)+" seconds")
    GPIO.output(blue, GPIO.HIGH)
    time.sleep(delay)
    GPIO.output(pin, True)
    print("pump off")
    GPIO.output(blue, GPIO.LOW)
    readLevel(3)
    
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    readLevel(3)
    client.subscribe("pub/pump-1")
    #checkCup(3)

def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    txt = str(msg.payload)
    msgText =  txt.split("'")
    #print(msgText[1])

    # drink sizes
    if msgText[1] == "s":
        print("Received order : small drink")
        if(checkLevel(3) == True):
            if(checkCup(3) == "CORRECT"):
                turnOn(1)
            else:
                print("Cup not placed correctly")
        else:
            print("Error : tank empty")
    elif msgText[1] == "m":
        print("Received order : medium drink")
        if(checkLevel(3) == True):
            if(checkCup(3) == "CORRECT"):
                turnOn(1.8)
            else:
                print("Cup not placed correctly")
        else:
            print("Error : tank empty")
    elif msgText[1] == "l":
        print("Received order : large drink")
        if(checkLevel(3) == True):
            if(checkCup(3) == "CORRECT"):
                turnOn(2.6)
            else:
                print("Cup not placed correctly")
        else:
            print("Error : tank empty")
    elif msgText[1] == "readLevel":
        print("Checking levels")
        readLevel(2)

def checkLevel(delay):
    if(readLevel(delay) != "EMPTY"):
        return True
    else:
        return False
    #return True

def readLevel(delay):
    i = 0
    while i < delay:
        GPIO.output(TRIG, False)
        time.sleep(refreshTime)
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO)==0:
            pulse_start = time.time()

        while GPIO.input(ECHO)==1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 1)
        print(distance)

        i += 1

    if(distance >= 1 and distance < 3.5):
        print("Drinks capacity : HIGH")
        publish.single("pub/tank-1", "HIGH", hostname="broker.emqx.io")
        GPIO.output(green, GPIO.HIGH)
        GPIO.output(yellow, GPIO.LOW)
        return "HIGH"
    elif(distance > 3.4 and distance < 4.2):
        print("Drinks capacity : MID")
        publish.single("pub/tank-1", "MID", hostname="broker.emqx.io")
        GPIO.output(green, GPIO.HIGH)
        GPIO.output(yellow, GPIO.LOW)
        return "MID"
    elif(distance >= 4.2 and distance < 4.8):
        print("Drinks capacity : LOW")
        publish.single("pub/tank-1", "LOW", hostname="broker.emqx.io")
        GPIO.output(green, GPIO.LOW)
        GPIO.output(yellow, GPIO.HIGH)
        return "LOW"
    elif(distance >= 4.8 and distance < 7):
        print("Drinks capacity : EMPTY")
        publish.single("pub/tank-1", "EMPTY", hostname="broker.emqx.io")
        GPIO.output(green, GPIO.LOW)
        GPIO.output(yellow, GPIO.HIGH)
        return "EMPTY"
    
def checkCup(delay):
    i = 0
    while i < delay:
        GPIO.output(TRIG2, False)
        time.sleep(refreshTime)
        GPIO.output(TRIG2, True)
        time.sleep(0.00001)
        GPIO.output(TRIG2, False)

        while GPIO.input(ECHO2)==0:
            pulse_start = time.time()

        while GPIO.input(ECHO2)==1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 1)
        #print(distance)

        i += 1

    if(distance >= 3.3 and distance <= 6):
        print("Cup placement : CORRECT")
        #publish.single("pub/tank-1", "HIGH", hostname="broker.emqx.io")
        GPIO.output(red, GPIO.LOW)
        return "CORRECT"
    else:
        print("Cup placement : INCORRECT")
        #publish.single("pub/tank-1", "HIGH", hostname="broker.emqx.io")
        GPIO.output(red, GPIO.HIGH)
        return "INCORRECT"

# Create an MQTT client and attach our routines to it.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()

GPIO.cleanup()
