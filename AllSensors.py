# -*- coding: utf-8 -*
import pigpio
import time



#pi cam code
import picamera
# camera =picamera.PiCamera()
# camera.resolution=(800,600)
# camera.start_preview()
# sleep(5)
# camera.capture('snapshot.jpg',resize=(640,480))
# camera.stop_preview()


imcount=0
RX = 23 #lidar gpio 23 so pin 16

pi = pigpio.pi()
pi.set_mode(RX, pigpio.INPUT)
pi.bb_serial_read_open(RX, 115200) 

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
						distance = recv[i+2] + recv[i+3] * 256
						strength = recv[i+4] + recv[i+5] * 256
						if distance <= 1200 and strength < 2000:
							if count>0 and prev !=distance
								camera =picamera.PiCamera()
								camera.resolution=(800,600)
								camera.start_preview()
								sleep(1)
								camera.capture('snapshot'+str(imcount)+'.jpg',resize=(640,480))
								camera.stop_preview()
							print(distance, strength) 
							imcount =imcount+1
							prev=distance
						#else:
							# raise ValueError('distance error: %d' % distance)	
						#i = i + 9

if __name__ == '__main__':
	try:
		getTFminiData()
	except:  
		pi.bb_serial_read_close(RX)
		pi.stop()
 