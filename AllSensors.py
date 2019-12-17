# -*- coding: utf-8 -*
#!/usr/bin/env
import pigpio
import RPi.GPIO as GPIO
import time
import os
import gpiozero
from gpiozero import LightSensor, Buzzer


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

LidarDefault=0
LidarThreshold=5
Lidarcnt=0
UltrasonicDefault=0
UltrasonicThreshold=5
ultracnt=0

def getTFminiData():
   # print("lidar")
    global LidarDistance
    global LightValue
    global UltrasonicDistance
    global prevUltraDist
    global prevLidVal
    global prevLight

    global LidarDefault
    global LidarThreshold
    global Lidarcnt



    count = 0

    while True:
        #print("#############")
        #time.sleep(0.05)   #change the value if needed
        time.sleep(1)
        #print("in while")
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
                        if(Lidarcnt==0):
                            LidarDefault=dist
                            Lidarcnt=Lidarcnt+1
                        #strength = recv[i+4] + recv[i+5] * 256
                        if(abs(dist-prevLidVal)>5):
                            #print("lidar if")
                            LidarDistance=dist
                            print("Lidar "+LidarDistance)
                            prevLidVal=dist
                            return
                        else:
                            #print("lidar else")
                            prevLidVal=dist

                            if count > 100:
                                return
                        


                        #else:
                            # raise ValueError('distance error: %d' % distance) 
                        #i = i + 9

def getUltraSonicData():
   # print("ultrasonic")
    global LidarDistance
    global LightValue
    global UltrasonicDistance
    global prevUltraDist
    global prevLidVal
    global prevLight

    global UltrasonicDefault
    global UltrasonicThreshold
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
            if (ultracnt==0):
                UltrasonicDefault=distance
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
    #print("light")
    global LidarDistance
    global LightValue
    global UltrasonicDistance
    global prevUltraDist
    global prevLidVal
    global prevLight

    while True:
        #print("Value: " + str(ldr.value))
      #  print("in Light While")
        light = ldr.value
        if(abs(light-prevLight)>0.2):
           # print("in Light IF")
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

    global UltrasonicDefault
    global UltrasonicThreshold
    global LidarThreshold
    global LidarDefault
  #  print("in main")

    while True:
       # print("Beginning of while Main")
        getTFminiData()
        getUltraSonicData()
        getLightData()
        GPIO.cleanup()
       # print("in Main while")
       # print("Still in main While")
        if (UltrasonicDefault-UltrasonicDistance>= UltrasonicThreshold or 
            LidarDefault-LidarDistance>= LidarThreshold or LightValue>0.4):
            print("evaluation")
            os.system("fswebcam -r 1280x720 image.jpg")
       # print("end")

if __name__ == '__main__':
    try:
       # print("Entering main")
        main()

    except:
        pi.bb_serial_read_close(RX)
        pi.stop() 
