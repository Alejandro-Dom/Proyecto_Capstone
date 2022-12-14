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
import serial
import RPi.GPIO as GPIO
import adafruit_fingerprint

#Pin = 20
#pin = 21
servo = 17
GPIO.setmode(GPIO.BCM)
#GPIO.setup(pin, GPIO.OUT)
#GPIO.setup(Pin, GPIO.OUT)
GPIO.setup(servo, GPIO.OUT)
p = GPIO.PWM(servo,50) #GPIO 17 para PWM con 50 Hz
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

# pylint: disable=too-many-statements
def enroll_finger(location):
    """Toma 2 imagenes del dedo y lo modela, luego lo guarda'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Coloca tu dedo en el sensor...", end="")
        else:
            print("Coloca el mismo dedo otra vez...", end="")

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Imagen tomada")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Error de imagen")
                return False
            else:
                print("Otro error")
                return False

        print("Modelando..", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Se completo la modelación")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Imagen mala")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("No se pudo identificar las características")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Imagen inválida")
            else:
                print("Otro error")
            return False

        if fingerimg == 1:
            print("Quita tu dedo")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creando modelo...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Creado")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("No coinciden")
        else:
            print("Otro error")
        return False

    print("Guardando modelo #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Guardadi")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Mala ubicación de almacenamiento")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Error de almacenamiento flash")
        else:
            print("Otro error")
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


while True:
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Error al leer los modelos")
    print("Modelos de huellas dactilares: ", finger.templates)
    if finger.count_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Error al leer los modelos")
    print("Cantidad de modelos encontrados: ", finger.template_count)
    if finger.read_sysparam() != adafruit_fingerprint.OK:
        raise RuntimeError("Error al obtener parámetros del sistema")
    print("Tamaño de la biblioteca de modelos: ", finger.library_size)
    print("1) Dar de alta una huella")
    print("2) Encontrar huella")
    print("3) Borrar huella")
    print("4) Limpiar biblioteca")
    print("5) Salir")
    print("----------------")
    c = input("> ")

    if c == "1":
        enroll_finger(get_num(finger.library_size))
    if c == "2":
        if get_fingerprint():
            print("Huella detectada con ID #", finger.finger_id, "con valor de confianza =", finger.confidence)
            """GPIO.output(Pin, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(Pin, GPIO.LOW)"""
            p.ChangeDutyCycle(2.5)
        else:
            print("Huella no encontrada")
            """GPIO.output(pin, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(pin, GPIO.LOW)"""            
    if c == "3":
        if finger.delete_model(get_num(finger.library_size)) == adafruit_fingerprint.OK:
            print("Borrado")
        else:
            print("Error al borrar")
    if c == "4":
        if finger.empty_library() == adafruit_fingerprint.OK:
            print("Biblioteca vacía")
        else:
            print("Error al vacirar la biblioteca")
    if c == "5":
        print("Adiós")
        p.stop()
        GPIO.cleanup()
        raise SystemExit