# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# Este programa sirve para controlar el acceso
# Lee la huella dactilar del usuario y manda un mensaje
# de confirmación por mqtt 
# Ultima modificación por: Alejandro Domínguez Ramírez y Luis Manuel Sanchez Vivar
# el 01 de diciembre del 2022
"""
Conexión Hardware
            As608 --- RPi4
(rojo)      Vc   ---  3.3 V 
(negro)     GND  ---  GND   
(amarillo)  Tx   ---  GPIO15
(blanco)    Rx   ---  GPIO14
"""
#Bibliotecas
import time
from time import sleep
import serial
import RPi.GPIO as GPIO
import adafruit_fingerprint
import paho.mqtt.client as mqtt

LEDV = 27
LEDR = 22
servo = 17
buzz = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEDR, GPIO.OUT)
GPIO.setup(LEDV, GPIO.OUT)
GPIO.setup(servo, GPIO.OUT)
GPIO.setup(buzz, GPIO.OUT, initial = GPIO.LOW)
p = GPIO.PWM(servo,50) #GPIO 17 para PWM con pulso de 50 Hz
p.start(2.5)
pin = ""

# Usando con Linux/Raspberry Pi 4 y hardware UART:
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

#Se crea el objeto finger
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

#################Funciones#################################


def get_fingerprint():
    """Se obtiene una imagen de huella dactilar, se hace un modelo y se compara"""
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
    """Se usa input() para obtener un número válido de 0 al tamaño máximo
     de la biblioteca"""
    i = -1
    while (i > max_number - 1) or (i < 0):
        try:
            i = int(input("Ingresa un ID # desde 0-{}: ".format(max_number - 1)))
        except ValueError:
            pass
    return i

def on_connect (client,userdata,flags,rc):
    print("Se conectó con mqtt")

def enviarmqtt(tema, mensaje, host = "broker.hivemq.com", Puerto = 1883):
    client.publish(tema, mensaje)

#Función para recibir el pin de acceso generado por el ESP32
def on_message(client, userdata, msg):
    global pin
    if msg.topic == "Capstone/Caja_Seguridad_Biometrica/MADS/Confirmacion":
        pin=(msg.payload.decode("utf-8"))
        print (pin)

client = mqtt.Client()
client.on_connect = on_connect
client.connect("broker.hivemq.com",1883,60)
client.loop_start()
time.sleep(3)

print("Ingresa la contraseña")
print(keypad)
if(keypad == "True"):
    try:
        print("Ponga su dedo sobre el escaner")
        if get_fingerprint():
            print("Huella detectada con ID #", finger.finger_id, "con valor de confianza =", finger.confidence)
            GPIO.output(LEDV, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(LEDV, GPIO.LOW)
            enviarmqtt("Capstone/Caja_Seguridad_Biometrica/MADS/Confirmacion","Seguro abierto")
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
        GPIO.cleanup()
        p.stop()
        raise SystemExit
    except KeyboardInterrupt:         
        print("Adiós")
        p.stop()
        GPIO.cleanup()
        client.loop_stop()
        client.disconnect()
        raise SystemExit
