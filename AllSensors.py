# -*- coding: utf-8 -*
#!/usr/bin/env
import pigpio
import RPi.GPIO as GPIO
import time
import os
from gpiozero import LightSensor, Buzzer


#pi cam code
import picamera
# camera =picamera.PiCamera()
# camera.resolution=(800,600)
# camera.start_preview()
# sleep(5)
# camera.capture('snapshot.jpg',resize=(640,480))
# camera.stop_preview()


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

def getTFminiData():
    while True:
        #print("#############")
        #time.sleep(0.05)   #change the value if needed
        time.sleep(1)
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
                        #strength = recv[i+4] + recv[i+5] * 256
                        if(abs(dist-prevLidVal)>5):
                            LidarDistance=dist
                            print(LidarDistance)
                            prevLidVal=dist
                        else:
                            prevLidVal=dist 
                        imcount =imcount+1
                        prev=distance
                        #else:
                            # raise ValueError('distance error: %d' % distance) 
                        #i = i + 9

def getUltraSonicData():
    while True:
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
        if(abs(distance-prevUltraDist)>2):
            UltrasonicDistance=distance
            print("UltrasonicDistance:",UltrasonicDistance,"cm")
            prevUltraDist=UltrasonicDistance
        else:
            prevUltraDist=UltrasonicDistance

    #allow keyboard interrupt to stop program

def getLightData():
    while True:
        #print("Value: " + str(ldr.value))
        light = ldr.value
        if(abs(light-prevLight)>0.2):
            LightValue=light
            prevLight=light
        else:
            prevLight=light

if __name__ == '__main__':
    try:
        while True:
            getTFminiData()
            getUltraSonicData()
            getLightData()

        if (UltrasonicDistance<= 10 | LidarDistance<= 10 | LightValue>0.4):
            os.system("fswebcam -r 1280x720 image.jpg")



    except:  
        pi.bb_serial_read_close(RX)
        pi.stop()
 
