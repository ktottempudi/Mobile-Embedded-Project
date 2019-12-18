# -*- coding: utf-8 -*
#!/usr/bin/env
import pigpio
import RPi.GPIO as GPIO
import time
import os
import gpiozero
from gpiozero import LightSensor, Buzzer
from twilio.rest import Client
import smtplib
import imgix

#pi cam code

# camera =picamera.PiCamera()
# camera.resolution=(800,600)
# camera.start_preview()
# sleep(5)
# camera.capture('snapshot.jpg',resize=(640,480))
# camera.stop_preview()

GPIO.setmode(GPIO.BOARD)
ldr = LightSensor(4)
imcount=0
RX = 23 #lidar gpio 23 so pin 16

pi = pigpio.pi()
pi.set_mode(RX, pigpio.INPUT)
pi.bb_serial_read_open(RX, 115200) 

LidarDistance = 0
LightValue = 0
UltrasonicDistance = 0
prevUltraDist = 0
prevLidVal = 0
prevLight = 0

ultradefault=0
ultracnt=0
lidardefault=0
lidarcnt=0
lightdefault=0
lightcnt=0

def getTFminiData():
    global LidarDistance
    global LightValue
    global UltrasonicDistance
    global prevUltraDist
    global prevLidVal
    global prevLight
    global lidardefault
    global lidarcnt

    count = 0

    while True:
        #print("#############")
        #time.sleep(0.05)   #change the value if needed
        time.sleep(1)

        count = count + 1
        (count, recv) = pi.bb_serial_read(RX)
        if count > 8:
            for i in range(0, count-9):
                if recv[i] == 89 and recv[i+1] == 89: # 0x59 is 89
                    checksum = 0
                    for j in range(0, 8):
                        checksum = checksum + recv[i+j]
                    checksum = checksum % 256
                    if checksum == recv[i+8]:
                        #LidarDistance = recv[i+2] + recv[i+3] * 256
                        dist = recv[i+2] + recv[i+3] * 256
                        if(lidarcnt==0):
                            lidardefault=dist
                            lidarcnt=ultracnt+1
                        #strength = recv[i+4] + recv[i+5] * 256
                        if(abs(dist-prevLidVal)>5):
                            LidarDistance=dist
                            print("Lidar Distance: ")
                            print(LidarDistance)
                            prevLidVal=dist
                            return
                        else:
                            prevLidVal=dist

                            if count > 100:
                                return
                        


                        #else:
                            # raise ValueError('distance error: %d' % distance) 
                        #i = i + 9

def getUltraSonicData():

    global LidarDistance
    global LightValue
    global UltrasonicDistance
    global prevUltraDist
    global prevLidVal
    global prevLight
    global ultradefault
    global ultracnt


    while True:
        try:
            GPIO.setmode(GPIO.BOARD)
            #assign gpio pin numbers to trigger&echo
            PIN_TRIGGER = 13
            PIN_ECHO = 11

            #assign trigger&echo to proper gpio i/o status
            GPIO.setwarnings(False)
            GPIO.setup(PIN_TRIGGER, GPIO.OUT)
            GPIO.setup(PIN_ECHO, GPIO.IN)

            #set trigger to low
            GPIO.output(PIN_TRIGGER, GPIO.LOW)

            #sensor calibration/settle time
            time.sleep(1.4)

            #set trigger to high
            GPIO.output(PIN_TRIGGER, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(PIN_TRIGGER, GPIO.LOW)

            #condition to set start/stop time based on echo
            while GPIO.input(PIN_ECHO)==0:
                pulse_start_time = time.time()
            while GPIO.input(PIN_ECHO)==1:
                pulse_end_time = time.time()

            #calculate distance based on times. assume speed of sound to  be 17150 cm/s. round distance to 2 decimal places
            pulse_duration = pulse_end_time - pulse_start_time
            distance = round(pulse_duration * 17150, 2)
            if(ultracnt==0):
                ultradefault=distance
                ultracnt=ultracnt+1
            if(abs(distance-prevUltraDist)>2):
                UltrasonicDistance=distance
                print("UltrasonicDistance:",UltrasonicDistance,"cm")
                prevUltraDist=UltrasonicDistance
                break
            else:
                prevUltraDist=UltrasonicDistance
                break

        except:
            print("stopped")

            break
    #allow keyboard interrupt to stop program

def getLightData():

    global LidarDistance
    global LightValue
    global UltrasonicDistance
    global prevUltraDist
    global prevLidVal
    global prevLight
    global lightdefault
    global lightcnt

    while True:
        #print("Value: " + str(ldr.value))
        light = ldr.value
        if (lightcnt==0):
            lightdefault=light
            lightcnt=lightcnt+1
        if(abs(light-prevLight)>0.2):

            LightValue=light
            prevLight=light
            break
        else:
            prevLight=light
            break

def main():

    global LidarDistance
    global LightValue
    global UltrasonicDistance
    global prevUltraDist
    global prevLidVal
    global prevLight
    global lidardefault
    global lidarcnt
    global ultradefault
    global ultracnt
    global lightdefault
    global lightcnt


    
    account_sid = "ACc8cf1d03de8d5e278131f7c16602da8d"
    auth_token  = "ecf0c95be902670acd9e89e83b3f3364"
    client = Client(account_sid, auth_token)
    
    while True:
        getTFminiData()
        getUltraSonicData()
        getLightData()
        GPIO.cleanup()
        #print("in Main while")
        #print("Still in main While")
        if (ultradefault-UltrasonicDistance> 10 or lidardefault-LidarDistance> 10 or lightdefault-LightValue>0.4):
            #print("evaluation")
            os.system("fswebcam -r 1280x720 image.jpg")
            builder = imgix.UrlBuilder("demos.imgix.net")
            builder.create_url("/image.jpg", {'w':1280, 'h':720})

            message = client.messages \
            .create(body='Home security system', 
                    from_='+18086703472',
                    to='+17324849120'
                    )


  
            #print(msg.as_string())
            #print(message.sid)




if __name__ == '__main__':
    try:
        print("Entering main")
        main()

    except:
        pi.bb_serial_read_close(RX)
        pi.stop() 
