# Este programa sirve para controlar el acceso
# Lee la huella dactilar del usuario, recibe el pin mediante una conexión con MQTT
# y lee las teclas presionadas por el usario,
# hace una comparación y envia una señal al servomotor
# para abrir la compuerta de la caja biométrica
# Ultima modificación por: Alejandro Domínguez Ramírez y Luis Manuel Sanchez Vivar
# el 01 de diciembre del 2022
"""
Conexión Hardware 
            As608 --- RPi4                  Buzzer  --- Rpi4
(rojo)      Vc   ---  3.3 V                     +   --- GPIO 23
(negro)     GND  ---  GND                       -   --- GND
(amarillo)  Tx   ---  GPIO15
(blanco)    Rx   ---  GPIO14

            Teclado --- RPi4                LED verde   --- RPi4
            L1      --- GPIO 5                  +       --- GPIO 27
            L2      --- GPIO 6                  -       --- GND
            L3      --- GPIO 13
            L4      --- GPIO 19
            C1      --- GPIO 12             LED rojo    --- RPi4
            C2      --- GPIO 16                 +       --- GPIO 22
            C3      --- GPIO 20                 -       --- GND
            C4      --- GPIO 21

            Servomotor --- RPi4
(rojo)          Vcc        ---  5 V
(naranja)       Data       ---  GPIO 17
(negro)         GND        ---  GND  
"""
#Bibliotecas
import time
from time import sleep
import serial
import RPi.GPIO as GPIO
import adafruit_fingerprint
import paho.mqtt.client as mqtt

#Asignación de pines
LEDV = 27
LEDR = 22
servo = 17
buzz = 23
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEDR, GPIO.OUT)
GPIO.setup(LEDV, GPIO.OUT)
GPIO.setup(servo, GPIO.OUT)
GPIO.setup(buzz, GPIO.OUT, initial = GPIO.LOW)
p = GPIO.PWM(servo,50) #GPIO 17 para PWM con pulso de 50 Hz
p.start(7)
pin = ""

# Usando con Linux/Raspberry Pi 4 y hardware UART:
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

#Se crea el objeto finger
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

#################Funciones#################################


def get_fingerprint():
    #Se obtiene una imagen de huella dactilar, se hace un modelo y se compara
    print("Esperando la imagen..")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Modelando...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Buscando...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True
##################################################


def get_num(max_number):
    #Se usa input() para obtener un número válido de 0 al tamaño máximo de la biblioteca
    i = -1
    while (i > max_number - 1) or (i < 0):
        try:
            i = int(input("Ingresa un ID # desde 0-{}: ".format(max_number - 1)))
        except ValueError:
            pass
    return i

#Función para recibir el pin de acceso generado por el ESP32
def on_connect(client, userdata,flags,rc):
    print("Se conecto con mqtt " + str(rc))
    client.subscribe("Capstone/Caja_Seguridad_Biometrica/MADS/Confirmacion")
def on_message(client, userdata, msg):
    if msg.topic == "Capstone/Caja_Seguridad_Biometrica/MADS/Confirmacion":
        pin=(msg.payload.decode("utf-8"))
        print (pin)
        if (pin == "True"):
            print("Ponga su dedo sobre el escaner")
            if get_fingerprint():
                print("Huella detectada con ID #", finger.finger_id, "con valor de confianza =", finger.confidence)
                GPIO.output(LEDV, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(LEDV, GPIO.LOW)
                p.ChangeDutyCycle(12)
                time.sleep(0.5)
                p.ChangeDutyCycle(0)
            else:
                print("Huella no encontrada")
                GPIO.output(LEDR, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(LEDR, GPIO.LOW)
                while True:
                    GPIO.output(buzz, GPIO.HIGH)
                    sleep(0.3)
                    GPIO.output(buzz, GPIO.LOW)
                    sleep(0.3) 
        else:
            print("Pin incorrecto")
            print("Adios")
            p.stop()
            GPIO.cleanup()
            raise SystemExit
        
client=mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com",1883,60)
client.loop_forever()