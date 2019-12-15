# -*- coding: utf-8 -*
#!/usr/bin/env
import pigpio
import RPi.GPIO as GPIO
import time
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

def getTFminiData():
	while True:
		#print("#############")
		#time.sleep(0.05)	#change the value if needed
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
						UltrasonicDistance = recv[i+2] + recv[i+3] * 256
						strength = recv[i+4] + recv[i+5] * 256
						if UltrasonicDistance <= 1200 and strength < 2000:
							if count>0 and prev !=distance
								camera =picamera.PiCamera()
								camera.resolution=(800,600)
								camera.start_preview()
								sleep(1)
								camera.capture('snapshot'+str(imcount)+'.jpg',resize=(640,480))
								camera.stop_preview()
							#print(distance, strength) 
							imcount =imcount+1
							prev=distance
						#else:
							# raise ValueError('distance error: %d' % distance)	
						#i = i + 9

def getUltraSonicData():
    while True:
    try:
        GPIO.setmode(GPIO.BOARD)
        #assign gpio pin numbers to trigger&echo
        PIN_TRIGGER = 13
        PIN_ECHO = 11
        prevDist = 0

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
        if(distance!=prevDist):
            print("Distance:",distance,"cm")
            prevDist=distance
        else:
            prevDist=distance

    #allow keyboard interrupt to stop program
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
        break

def getLightData():
    while True:
	    print("Value: " + str(ldr.value))

if __name__ == '__main__':
	try:
		getTFminiData()
	except:  
		pi.bb_serial_read_close(RX)
		pi.stop()
 
