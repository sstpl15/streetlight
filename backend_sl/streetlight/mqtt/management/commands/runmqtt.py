# mqtt/management/commands/runmqtt.py
import json
import paho.mqtt.client as mqtt_client
from django.http import HttpResponse,JsonResponse
from rest_framework.response import Response
import base64
from django.core.management.base import BaseCommand
from django.conf import settings
import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta,date
from django.utils import timezone
import pytz
from api.models import payloaddata,payload_power_mst


# Now you can use the pytz module


class Command(BaseCommand):
    help = 'Run MQTT client to receive data from MQTT broker'

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.stdout.write(self.style.SUCCESS("Connected to MQTT Broker!"))
        else:
            self.stderr.write(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload=msg.payload.hex()
            print('payload:',payload)
        except UnicodeDecodeError:
            # If decoding as UTF-8 fails, handle it as a binary sequence
            payload = msg.payload.decode('utf-8')
            print("Decoded payload:", payload)
            

        if str(payload) in ['0000043041434b','41434b',' 0000043000']:
            print('Pass')
            pass
        else:
            devEui=payload[0:8]
            print('devEui:',devEui)
            final_payload=payload[8:]
            print('final_payload:',final_payload)
            return Response(final_payload)
        response_message = {'res': 'data received'}
        response_json = json.dumps(response_message)

        # client.publish(settings.MQTT_RESPONSE_TOPIC, response_json)

    def connect_mqtt(self) -> mqtt_client:
        client = mqtt_client.Client()
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        client.on_connect = self.on_connect
        client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
        return client

    def subscribe(self, client: mqtt_client):
        client.subscribe('uplink')
        client.on_message = self.on_message

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting MQTT client..."))
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_forever()

    def publish_cmd(self,request,send_command):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client()
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        client.on_connect = self.on_connect
        client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
        print('send_command:',send_command)
        print(type(send_command))
        
        client.publish(settings.MQTT_RESPONSE_TOPIC, send_command)
        print("yes command send")
        client.disconnect()

        return HttpResponse('downlinksend')












# 00000430    181102624c44120012053212015012026312033c125028633c0000000000000000
# d810503e0324183006003219505020306300003c0200280f0f000052300943000000002654120175476142









 





# import time
# import paho.mqtt.client as mqtt
# from django.core.management.base import BaseCommand
# from django.conf import settings

# class Command(BaseCommand):
#     help = 'Run MQTT client to receive data from MQTT broker'

#     def on_connect(self, client, userdata, flags, rc):
#         if rc == 0:
#             self.stdout.write(self.style.SUCCESS('Connected to MQTT broker!'))
#             client.subscribe('topic')  # Replace 'topic' with the topic you want to subscribe to
#         else:
#             self.stderr.write('Failed to connect to MQTT broker')

#     def on_message(self, client, userdata, msg):
#         data = msg.payload.decode()
#         # Process the data received from the MQTT broker
#         self.stdout.write(self.style.SUCCESS(f'Received data: {data}'))

#     def handle(self, *args, **kwargs):
#         client = mqtt.Client()
#         client.on_connect = self.on_connect
#         client.on_message = self.on_message
#         client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
#         client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, keepalive=60)

#         try:
#             self.stdout.write(self.style.SUCCESS('Starting MQTT client...'))
#             client.loop_forever()
#         except KeyboardInterrupt:
#             self.stdout.write(self.style.SUCCESS('MQTT client stopped by user.'))
