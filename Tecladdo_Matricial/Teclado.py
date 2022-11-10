import RPi.GPIO as GPIO
from time import sleep

Nopres = 0
Pres  = 1

botones = [['1', '2', '3', 'A'], ['4', '5', '6', 'B'], ['7', '8', '9', 'C'], ['*', '0', '#', 'D']]

#Pines GPIO Raspberry
filas = [2,3,4,5]
columnas = [6,7,8,9]

#Se definen los pines de las columnas como entradas y los pines de filas como salidas
for i in range (4):
    GPIO.setup(filas[i], GPIO.OUT)

for j in range (4):
    GPIO.setup(columnas[j], GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def init():
    for fila in range(0,4):
        for columna in range (0,4):
            GPIO.output(filas,GPIO.LOW)
            #fila_pin[fila].low()

def escan(fila,columna):
    """Escanea todo el teclado"""

    #Se define la columna actual en alto
    GPIO.output(filas,GPIO.HIGH)
    #fila_pin[fila].hihg()
    tecla = None

    #Se realiza una verificación para saber si hay una tecla presionada
    if GPIO.input[columnas] == Nopres:
    #if columna_pin[columna].value() == Nopres:
        tecla = Nopres
    else:
        tecla = Pres
    GPIO.output[filas,GPIO.LOW]
    #fila_pin[fila].low()

    #Se regresa el estado de la tecla
    return tecla

Contra = "147258369"
entrada = ""
print("Ingrese su pin de acceso")

#Se definen las columnas en bajo
init()

while True:
    for fila in range(4):
        for columna in range (4):
            tecla = escan(fila,columna)
            if tecla == Nopres:
                print("Tecla presionada", botones[fila][columna])
                sleep(0.5)
                last_tecla = botones[fila][columna]
                entrada = entrada + last_tecla
                if len(entrada) == 6:
                    if entrada == Contra:
                        print("Contraseña correcta, puede continuar")
                        entrada = ""
                    else:
                        print("Contraseña incorrecta, acceso bloqueado")
                        entrada = ""
