# Proyecto_Capstone: Caja de Seguridad biométrica

## Descripción
Se le conoce como seguridad biométrica al uso de la biometría para proteger y proporcionar robustez a dispositivos, instalaciones o cualquier tipo de información confidencial, estableciendo un mayor grado de protección respecto a métodos tradicionales. Nuestra caja de seguridad utilizará las huellas dactilares del usuario y un código numérico de 6 dígitos, que se genera cada cierto tiempo, para tener acceso al contenido.

## Justificación
Siempre ha existido una gran probabilidad de que los métodos de autenticación tradicionales puedan ser robados por estafadores.
Las soluciones biométricas garantizan un mayor nivel de protección, utilizando la identidad de un usuario como principal medio de autenticación para acceder a la información sensible, verificando aspectos tangibles como algo que el usuario tiene o algo que es.

## Objetivos Generales
Diseñar y programar una caja que utilice por lo menos un dato de la biometría del usuario para tener un producto ultra seguro. 
## Objetivos Específicos
    - Programar un senosro As608 de huella dactilar utilizando Python.
    - Programar un keypad matricial de 4x4 que pueda cambiar el pin de autorización cada cierto tiempo.
## Resultados Esperados
Se espera tener un producto totalmente funcional, el cual se pueda abrir solamente con los datos de un único usuario; en caso contrario, la caja se bloqueará y emitirá una alarma que no podrá ser desactivada.
# Material necesario
### Hardware
- RaspBerry Pi 4
- Placa de extensión para pines GPIO (Opcional)
- Protoboard
- Lector de huella dactilar As608 [(Ver Datasheet)](https://server4.eca.ir/eshop/000/AS608/Synochip-AS608.pdf) 
- Teclado matricial 4x4 de membrana [(Ver Datasheet)](http://www.electronicoscaldas.com/datasheet/Teclado-membrana-matricial-4x4.pdf)
- Buzzer
- Servomotor SG90 
- Cables dupont (macho-hembra)
- LED's
- ESP32-CAM
![](https://github.com/Alejandro-Dom/Proyecto_Capstone/blob/main/Imagenes/Materiales.png)
### Software y lenguajes
- Visual Studio Code
- VNC Viewer
- Python 3
- Arduino IDE
- MQTT
- Node-RED


## Instrucciones:
1. Revisar el curso en la página de CodigoIoT en el siguiente enlace: https://edu.codigoiot.com/course/view.php?id=978#section-1
2. Clonar el repositorio
     - <pre><code>git clone https://github.com/Alejandro-Dom/Proyecto_Capstone.git </code></pre>
3.  Revisar y realizar los ejemplos encontrados en la carpeta Ejemplos_sensores en el siguiente orden:
    - Mqtt_prueba.py
    - servotest.py
    - Teclado_Ej.py
    - As608_ejemplo_registro.py
4. Conectar el ESP32-CAM, cargar y ejecutar el código Generador_pin.ino
5. Inicar Node-RED e importar el flows.json y abrir los dashboards
6. En la primera Raspberry realizar las conexiones para el teclado matricial 4x4
7. En la segunda Raspberry realizar las conexiones y configuraciones del lector de huella dactilar
8. Ejecutar los códigos Teclado_Capstone.py y Caja_seguridad.py, en la primera y segunda Raspberry, respectivamente
## Desarrollado por:
- [Alejandro Domínguez Ramirez](https://github.com/Alejandro-Dom)
- [Luis Manuel Sánchez Vívar](https://github.com/ManuSV16)


