from gpiozero import LightSensor, Buzzer

ldr = LightSensor(4)

while True:
	print("Value: " + str(ldr.value))
