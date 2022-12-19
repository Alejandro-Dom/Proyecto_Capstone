import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

Filas=[5,6,13,19]
for i in range (4):
	GPIO.setup(Filas[i], GPIO.OUT)
	
Columnas=[12,16,20,21]
for j in range (4):
	GPIO.setup(Columnas[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def lectura(FILAS,CARACTERES):
	GPIO.output(FILAS,GPIO.HIGH)
	if (GPIO.input(Columnas[0])==1):
		print(CARACTERES[0])
	if (GPIO.input(Columnas[1])==1):
		print(CARACTERES[1])
	if (GPIO.input(Columnas[2])==1):
		print(CARACTERES[2])
	if (GPIO.input(Columnas[3])==1):
		print(CARACTERES[3])
	GPIO.output(FILAS,GPIO.LOW)
try:
	while True:
		lectura(Filas[0],["1","2","3","A"])
		lectura(Filas[1],["4","5","6","B"])
		lectura(Filas[2],["7","8","9","C"])
		lectura(Filas[3],["*","0","#","D"])
		sleep(0.16)#Sensibilidad 
except KeyboardInterrupt:
	print("\nEl programa termino")