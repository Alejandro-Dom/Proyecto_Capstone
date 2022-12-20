#  Este programa sirve para controlar el acceso
#  recibe el pin mediante una conexión con MQTT
#  y lee las teclas presionadas por el usario,
#  hace una comparación y envia una señal al servomotor
#  para abrir la compuerta de la caja biométrica
#  por: Luis Manuel Sanchez Vivar y Alejandro Domínguez Ramírez
#  el 19 de diciembre del 2022
import RPi.GPIO as GPIO
from gpiozero import LED
import paho.mqtt.client as mqtt
import time

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
#Led rojo y verde
Led_verde = LED(27)
Led_rojo = LED(22)
#Servomotor
GPIO.setup(17,GPIO.OUT)
servo1 = GPIO.PWM(17,50)
servo1.start(0)

# El -1 indica que no hay tecla presionada
keypadPressed = -1

pin = ""
input = ""

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)
GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
def on_connect(client, userdata,flags,rc):
    print("Se conecto con mqtt" + str(rc))
    client.subscribe("Capstone/Caja_Seguridad_Biometrica/MADS")
def enviarMQTT(tema,mensaje,host="broker.hivemq.com",Puerto=1883):
    client.publish(tema, mensaje)
def on_message(client, userdata, msg):
    global pin
    if msg.topic == "Capstone/Caja_Seguridad_Biometrica/MADS":
        pin=(msg.payload.decode("utf-8"))
        return pin
client=mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com",1883,60)
client.loop_start()
time.sleep(3)
# Esta función registra la tecla presionada
def keypadCallback(channel):
    global keypadPressed
    if keypadPressed == -1:
        keypadPressed = channel

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
        servo1.ChangeDutyCycle(2+(90/18))
        Led_verde.off()
        Led_rojo.off();
        pressed = True

    GPIO.output(L3, GPIO.LOW)
    GPIO.output(L1, GPIO.HIGH)

    if (not pressed and GPIO.input(C4) == 1):
        if input == pin:
            print("Contraseña correcta!")
            Led_verde.on()
            Led_rojo.off()
            servo1.ChangeDutyCycle(2+(0/18))
            enviarMQTT("Capstone/Caja_Seguridad_Biometrica/MADS/Confirmacion","True")
        
        else:
            print("Contraseña incorrecta!")
            Led_verde.off()
            Led_rojo.on()
        pressed = True

    GPIO.output(L3, GPIO.LOW)

    if pressed:
        input = ""

    return pressed

# reads the columns and appends the value, that corresponds
# to the button, to a variable
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
    print("\nApplication stopped!")
client.loop_stop()
client.disconnect()