from django.db import models
from datetime import datetime ,date
 

class user_registartion(models.Model):
    name=models.CharField(max_length=255)
    password=models.CharField(max_length=255)
    phone_no=models.CharField(max_length=12)
    email=models.EmailField()
    address=models.CharField(max_length=255)
    zone_name=models.CharField(max_length=255)
    designation=models.CharField(max_length=255)
    area_code=models.IntegerField()
    login_user_name=models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class BulkFile(models.Model):
    file=models.FileField(upload_to='files')

class Complaint(models.Model):
    date_of_complaint = models.DateTimeField()
    requester_name = models.CharField(max_length=100)
    requester_designation = models.CharField(max_length=50)
    device_eui = models.CharField(max_length=20)
    device_zone = models.CharField(max_length=30)
    device_pole_no = models.IntegerField()
    device_ward = models.CharField(max_length=20)
    issue_details = models.TextField()
    complaint_number = models.CharField(max_length=10,unique=True)

    def __str__(self):
        return self.device_eui



 

class maintenance(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    device_eui = models.CharField(max_length=100) 
    date_of_inspection = models.DateTimeField()
    inspector_name = models.CharField(max_length=100)
    device_latitude = models.CharField(max_length=20)
    device_longitude = models.CharField(max_length=20)
    device_pole_no = models.IntegerField()
    device_zone = models.CharField(max_length=20)
    check_choice = models.CharField(max_length=20)
    cleaned_choice = models.CharField(max_length=20)
    repaired_choice = models.CharField(max_length=20)
    device_replace = models.CharField(max_length=10)
    maintenance_status = models.CharField(max_length=20)
    issue_details = models.TextField()
    image = models.ImageField(upload_to="images", blank=True, null=True)
    complaint_number=models.CharField(max_length=20,null=True)


class Zone_details(models.Model):
    zone_name=models.CharField(max_length=50)
    def __str__(self):
        return self.zone_name 

class Ward_details(models.Model):
    # zone=models.ForeignKey(Zone_details, on_delete=models.CASCADE,related_name="zonename")
    zone_name=models.CharField(max_length=50)
    ward_name=models.CharField(max_length=50)
    def __str__(self):
        return self.ward_name

class LoRaServerDetails(models.Model):
    server_name=models.CharField(max_length=50)
    lora_version=models.CharField(max_length=50)
    user_name=models.CharField(max_length=50,blank=True,null=True)
    password=models.CharField(max_length=50,blank=True,null=True)
    lora_key=models.CharField(max_length=500,blank=True,null=True)
    def __str__(self):
        return self.server_name




class site_manager(models.Model):
    fk_server_name=models.ForeignKey(LoRaServerDetails,on_delete=models.CASCADE)
    server_name=models.CharField(max_length=100)
    site_name=models.CharField(max_length=50,unique=True)
    multicast_id=models.CharField(max_length=50)
    site_owner=models.CharField(max_length=50)

    def __str__(self):
        return self.site_name


        

class uplinkdata(models.Model):
    deveui=models.CharField(max_length=50)
    time_stamp=models.DateTimeField()
    gateway_mac=models.CharField(max_length=50)
    frequency=models.IntegerField()
    applicationName=models.CharField(max_length=100)
    dataRate=models.CharField(max_length=50)
    spreadingFactor=models.CharField(max_length=20)
    fCnt=models.CharField(max_length=20)
    rssi=models.CharField(max_length=20)
    snr=models.IntegerField()
    payload=models.CharField(max_length=255)


class device_register_details(models.Model):
    dev_eui = models.CharField(max_length=50, unique=True)
    device_zone = models.CharField(max_length=50)
    device_ward = models.CharField(max_length=50)
    pol_number = models.CharField(max_length=50)
    device_watt = models.IntegerField()
    device_type = models.CharField(max_length=50)
    device_category = models.CharField(max_length=50)
    device_latitude = models.CharField(max_length=20)
    device_longitude = models.CharField(max_length=20)
    dev_reg_date = models.DateField()
    site_name=models.CharField(max_length=50)
    server_name=models.CharField(max_length=50)
    multicast_add=models.CharField(max_length=150)

class payloaddata(models.Model):
    device = models.ForeignKey(device_register_details, on_delete=models.CASCADE)
    devEUI = models.CharField(max_length=100)
    dev_status = models.CharField(max_length=20,null=True,blank=True)
    luc_detail = models.CharField(max_length=50,null=True,blank=True)
    schedule_mode = models.CharField(max_length=50,null=True,blank=True)
    relay_status = models.CharField(max_length=100,null=True,blank=True)
    power_grid_fail = models.CharField(max_length=100,null=True,blank=True)
    lamp_fali = models.CharField(max_length=100,null=True,blank=True)
    command_action_status = models.CharField(max_length=100,null=True,blank=True)
    time_stamp = models.DateTimeField(null=True,blank=True)
    sch_start_time = models.TimeField(null=True,blank=True)
    sch_end_time = models.TimeField(null=True,blank=True)
    default_dimming = models.IntegerField(null=True,blank=True)
    first_slot_time = models.TimeField(null=True,blank=True)
    first_slot_dimming = models.IntegerField(null=True,blank=True)
    second_slot_time = models.TimeField(null=True,blank=True)
    second_slot_dimming = models.IntegerField(null=True,blank=True)
    third_slot_time = models.TimeField(null=True,blank=True)
    third_slot_dimming = models.IntegerField(null=True,blank=True)
    fourth_slot_time = models.TimeField(null=True,blank=True)
    fourth_slot_dimming = models.IntegerField(null=True,blank=True)
    meter_data_interval = models.IntegerField(null=True,blank=True)
    current_dimming = models.FloatField(null=True,blank=True)
    meter_kwh = models.FloatField(null=True,blank=True)
    meter_voltage = models.FloatField(null=True,blank=True)
    meter_current = models.FloatField(null=True,blank=True)
    latitude = models.CharField(max_length=20,null=True,blank=True)
    longitude = models.CharField(max_length=20,null=True,blank=True)

    def __str__(self):
        return self.devEUI

class payloaddatav4(models.Model):
    # device = models.ForeignKey(device_register_details, on_delete=models.CASCADE)
    devEUI = models.CharField(max_length=100,default='None')
    dev_status = models.CharField(max_length=20,default='None')
    luc_detail = models.CharField(max_length=50,default='None')
    schedule_mode = models.CharField(max_length=50,default='None')
    relay_status = models.CharField(max_length=100,default='None')
    power_grid_fail = models.CharField(max_length=100,default='None')
    lamp_fali = models.CharField(max_length=100,default='None')
    command_action_status = models.CharField(max_length=100,default='None')
    time_stamp = models.DateTimeField(default='None')
    sch_start_time = models.TimeField(default='None')
    sch_end_time = models.TimeField(default='None')
    default_dimming = models.IntegerField(default='None')
    first_slot_time = models.TimeField(default='None')
    first_slot_dimming = models.IntegerField(default='None')
    second_slot_time = models.TimeField(default='None')
    second_slot_dimming = models.IntegerField(default='None')
    third_slot_time = models.TimeField(default='None')
    third_slot_dimming = models.IntegerField(default='None')
    fourth_slot_time = models.TimeField(default='None')
    fourth_slot_dimming = models.IntegerField(default='None')
    meter_data_interval = models.IntegerField(default='None')
    current_dimming = models.FloatField(default='None')
    meter_kwh = models.FloatField(default='None')
    meter_voltage = models.FloatField(default='None')
    meter_current = models.FloatField(default='None')
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)

    def __str__(self):
        return self.devEUI

class payload_power_mst(models.Model):
    fk_device=models.ForeignKey(device_register_details,on_delete=models.CASCADE)
    device_eui=models.CharField(max_length=20)
    zone_name=models.CharField(max_length=50,blank=True, null=True)
    ward_name=models.CharField(max_length=50,blank=True, null=True)
    date=models.DateField()
    power_consume=models.CharField(max_length=100)
    power_save=models.CharField(max_length=100,blank=True, null=True)
    device_on_off=models.CharField(max_length=20)

    def __str__(self):
        return self.device_eui


class support_mst(models.Model):
    requester_name=models.CharField(max_length=100)
    requester_email=models.EmailField()
    requester_number=models.CharField(max_length=15)
    issue_details=models.TextField()

    def __str__(self):
        return self.requester_name