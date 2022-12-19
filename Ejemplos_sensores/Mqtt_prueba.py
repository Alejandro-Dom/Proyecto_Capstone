import paho.mqtt.client as mqtt
pin=""
def on_connect(client, userdata,flags,rc):
    print("Se conecto con mqtt" + str(rc))
    client.subscribe("Capstone/Caja_Seguridad_Biometrica/MADS")
def on_message(client, userdata, msg):
    if msg.topic == "Capstone/Caja_Seguridad_Biometrica/MADS":
        pin=(msg.payload.decode("utf-8"))
        print (pin)
client=mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com",1883,60)
client.loop_forever()
