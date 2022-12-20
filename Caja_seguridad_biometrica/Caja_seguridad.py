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
#from gpiozero import LED
import paho.mqtt.client as mqtt
#Se definen los pines de salida
LEDV = 27
LEDR = 22
servo = 17
buzz = 23
# Filas
L1 = 5
L2 = 6
L3 = 13
L4 = 19

# Columnas
C1 = 12
C2 = 16
C3 = 20
C4 = 21
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEDV, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(LEDR, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(servo, GPIO.OUT)
GPIO.setup(buzz, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)
GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
p = GPIO.PWM(servo,50) #GPIO 17 para PWM con pulso de 50 Hz
p.start(2.5)

# El -1 indica que no hay tecla presionada
keypadPressed = -1

pin = ""
input = ""

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
# Función para registrar la tecla presionada
def keypadCallback(channel):
    global keypadPressed
    if keypadPressed == -1:
        keypadPressed = channel

#Función para verificar la ocnexión con MQTT
def on_connect(client, userdata,flags,rc):
    print("Se conecto con mqtt" + str(rc))
    client.subscribe("Capstone/Caja_Seguridad_Biometrica/MADS")

#Función para enviar mensajes por MQTT
def enviarMQTT(tema,mensaje,host="broker.hivemq.com",Puerto=1883):
    client.publish(tema, mensaje)

#Función para recibir el pin de acceso generado por el ESP32
def on_message(client, userdata, msg):
    global pin
    if msg.topic == "Capstone/Caja_Seguridad_Biometrica/MADS":
        pin=(msg.payload.decode("utf-8"))
        return pin

client=mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client = mqtt.Client()
client.on_connect = on_connect
client.connect("broker.hivemq.com",1883,60)
client.loop_start()
time.sleep(3)

# Mandar un pulso cada que se presiona una tecla
GPIO.add_event_detect(C1, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C2, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C3, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C4, GPIO.RISING, callback=keypadCallback)

# Esta función da un estado a la teclas
def setAllLines(state):
    GPIO.output(L1, state)
    GPIO.output(L2, state)
    GPIO.output(L3, state)
    GPIO.output(L4, state)

def checkSpecialKeys():
    global input
    pressed = False

    GPIO.output(L3, GPIO.HIGH)

    if (GPIO.input(C4) == 1):
        print("Reset!")
        p.ChangeDutyCycle(2.5)
        GPIO.output(LEDV, GPIO.LOW)
        GPIO.output(LEDR, GPIO.LOW)
        pressed = True

    GPIO.output(L3, GPIO.LOW)
    GPIO.output(L1, GPIO.HIGH)

    if (not pressed and GPIO.input(C4) == 1):
        if input == pin:
            print("Contraseña correcta!")
            GPIO.output(LEDV, GPIO.HIGH)
            GPIO.output(LEDR, GPIO.LOW)
            p.ChangeDutyCycle(7)
            enviarMQTT("Capstone/Caja_Seguridad_Biometrica/MADS/Confirmacion","True")
        
        else:
            print("Contraseña incorrecta!")
            GPIO.output(LEDV, GPIO.LOW)
            GPIO.output(LEDR, GPIO.HIGH)
        pressed = True

    GPIO.output(L3, GPIO.LOW)

    if pressed:
        input = ""

    return pressed
def readLine(line, characters):
    global input
    # We have to send a pulse on each line to
    # detect button presses
    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        input = input + characters[0]
    if(GPIO.input(C2) == 1):
        input = input + characters[1]
    if(GPIO.input(C3) == 1):
        input = input + characters[2]
    if(GPIO.input(C4) == 1):
        input = input + characters[3]
    GPIO.output(line, GPIO.LOW)

try:
    print(pin)
    while True:
        # If a button was previously pressed,
        # check, whether the user has released it yet
        if keypadPressed != -1:
            setAllLines(GPIO.HIGH)
            if GPIO.input(keypadPressed) == 0:
                keypadPressed = -1
            else:
                time.sleep(0.1)
        # Otherwise, just read the input
        else:
            if not checkSpecialKeys():
                readLine(L1, ["1","2","3","A"])
                readLine(L2, ["4","5","6","B"])
                readLine(L3, ["7","8","9","C"])
                readLine(L4, ["*","0","#","D"])
                time.sleep(0.1)
            else:
                time.sleep(0.1)

except KeyboardInterrupt:
    print("Adios")
    p.stop()
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
    raise SystemExit