# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
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

Pin = 20
#pin = 21
servo = 18
buzz = 23
GPIO.setmode(GPIO.BCM)
#GPIO.setup(pin, GPIO.OUT)
GPIO.setup(Pin, GPIO.OUT)
GPIO.setup(servo, GPIO.OUT)
GPIO.setup(buzz, GPIO.OUT, initial = GPIO.LOW)
p = GPIO.PWM(servo,50) #GPIO 17 para PWM con pulso de 50 Hz
p.start(0)

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


try:
    print("Ponga su dedo sobre el escaner")
    if get_fingerprint():
        print("Huella detectada con ID #", finger.finger_id, "con valor de confianza =", finger.confidence)
        GPIO.output(Pin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(Pin, GPIO.LOW)
        p.ChangeDutyCycle(7)
    else:
        print("Huella no encontrada")
        """GPIO.output(pin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(pin, GPIO.LOW)""" 
        while True:
            GPIO.output(buzz, GPIO.HIGH)
            sleep(0.3)
            GPIO.output(buzz, GPIO.LOW)
            sleep(0.3) 
            GPIO.cleanup()
            raise SystemExit
except KeyboardInterrupt:         
    print("Adiós")
    p.ChangeDutyCycle(0)
    p.stop()
    GPIO.cleanup()
    raise SystemExit