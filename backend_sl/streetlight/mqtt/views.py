from django.shortcuts import render


# Create your views here.
from paho.mqtt import client as mqtt_client
import base64
import json
from django.http import HttpResponse  

 


broker = 'meters.siotel.in'
port = 1883
topic = "uplink"
response_topic = "downlink" 
# client_id = ''
username = 'vikram'
password = 'vikram@123'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client()
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(client)
        print(userdata)
        print(msg)
        # # if msg=='respone':
        # #     print('77777777777777777777777777777777777777')
        # print(msg.payload.decode())
        # data=msg.payload.decode()
        # parsed_data = json.loads(data)
        # devEUI = base64.b64decode(parsed_data['devEUI']).hex()
        # loRaSNR = parsed_data['rxInfo'][0]['loRaSNR']
        # rssi = parsed_data['rxInfo'][0]['rssi']
        # frequency = parsed_data['txInfo']['frequency']
        # modulation = parsed_data['txInfo']['modulation']
        # spreadingFactor = parsed_data['txInfo']['loRaModulationInfo']['spreadingFactor']

        # print("devEUI:", devEUI)
        # print("loRaSNR:", loRaSNR)
        # print("rssi:", rssi)
        # print("frequency:", frequency)
        # print("modulation:", modulation)
        # print("spreadingFactor:", spreadingFactor)

        response_message = {
            'res': 'data received'}
        
        response_json = json.dumps(response_message)

        # Publish the response message
        # client.publish(topic, response_json)
        client.publish(response_topic, response_json)
    client.subscribe(topic)
    client.on_message = on_message



def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


def publish_cmd(request,mac):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client()
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    



    message = [{'hello':'cmd'},{'bye':'cmd2'}]

    # Convert the message payload to JSON format
    message_json = json.dumps(message)

    # Publish the message
    topic='downlink/'+mac
    client.publish(topic, message_json)
    client.disconnect()

    return HttpResponse('downlinksend')