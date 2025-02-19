"""
This is a brief description of what this module does.

You can provide more details about the module's functionality, usage, and any important information here.
"""
from rest_framework import serializers
from .models import (
    LoRaServerDetails,
    site_manager,
    payloaddata,
    payload_power_mst,
    Zone_details,
    Ward_details,
    user_registartion,
    maintenance,
    device_register_details,
    Complaint,
    support_mst
    )
# create a serializer class
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=user_registartion
        fields='__all__'
class DeviceComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model=Complaint
        exclude = ('complaint_number',)

class MaintenanceSerializer(serializers.ModelSerializer):
    complaint_id = DeviceComplaintSerializer()
    class Meta:
        model=maintenance
        fields= [
        'complaint_id',
        'device_eui',
        'date_of_inspection',
        'inspector_name',
        'device_latitude',
        'device_longitude',
        'device_pole_no',
        'device_zone',
        'check_choice',
        'cleaned_choice',
        'repaired_choice',
        'device_replace',
        'maintenance_status',
        'issue_details',
        'image'
        ]

class DeviceRegisterDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model=device_register_details
        fields='__all__'


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model=Zone_details
        fields='__all__'

class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model=Ward_details
        fields='__all__'

class PayloadSerializer(serializers.ModelSerializer):
    class Meta:
        model=payloaddata
        fields=['devEUI','dev_status','luc_detail',
        'schedule_mode','relay_status','power_grid_fail','lamp_fali','command_action_status','time_stamp','sch_start_time',
        'sch_end_time','default_dimming','first_slot_time','first_slot_dimming','second_slot_time','second_slot_dimming',
        'third_slot_time','third_slot_dimming','fourth_slot_time','fourth_slot_dimming','meter_data_interval','current_dimming',
        'meter_kwh','meter_voltage','meter_current','latitude','longitude',
        ]


class PayloadMstSerializer(serializers.ModelSerializer):
    class Meta:
        model=payload_power_mst
        fields=['date', 'power_consume','power_save']

class LoRaServerSerializer(serializers.ModelSerializer):
    class Meta:
        model=LoRaServerDetails
        fields=['server_name','lora_version','user_name','password','lora_key']    
        
class SiteDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = site_manager  # Make sure your model name is correct
        fields = ['site_name', 'server_name', 'multicast_id', 'site_owner']


class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = support_mst
        fields = ['requester_name','requester_email','requester_number','issue_details']


 
