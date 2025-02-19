# your_project/utils.py
from mqtt.management.commands.runmqtt import Command

def call_publish_cmd(request,mac,command):
    mac_address =mac
    command_to_send =command
    runmqtt_command = Command()

    hex_string=mac_address[8:] + command_to_send
    send_command = bytes.fromhex(hex_string)

    return runmqtt_command.publish_cmd(request,send_command)
