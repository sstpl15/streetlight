from rest_framework.response import Response
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .serializers import (
    LoRaServerSerializer,
    SiteDetailsSerializer, 
    PayloadMstSerializer,
    ZoneSerializer,
    WardSerializer,
    PayloadSerializer,
    UserSerializer,
    MaintenanceSerializer,
    DeviceRegisterDetailsSerializer,
    DeviceComplaintSerializer,
    SupportSerializer,
    )
from .models import (
    site_manager,
    LoRaServerDetails,
    payload_power_mst,
    Zone_details,
    Ward_details,
    BulkFile,
    payloaddata,
    uplinkdata,
    payloaddatav4,
    user_registartion,
    device_register_details,
    Complaint,maintenance,
    support_mst
    )
from django.contrib.auth import authenticate,login,logout 
import numpy as np
import pandas as pd
from datetime import date
import datetime
from datetime import datetime
import time
import codecs
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from collections import OrderedDict
import threading
import json
import base64
import requests
from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.parsers import JSONParser
from django.db.models import F, Q, Max,FloatField,Case, When, Value,CharField,IntegerField,Sum,Count
from django.db.models.functions import Greatest,Coalesce,ExtractHour
import calendar
from subprocess import run
 
 
def send_email(request):
    subject = 'Hello from Django!'
    message = 'This is a test email sent from Django.'
    from_email = 'test@gmail.com'
    recipient_list = ['test@gmail.com', 'recipient2@example.com']
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    return HttpResponse('Email sent!')

'''Application Login Api that recived post request and send responce ok or 200 status code else return BAD_REQUEST'''
class loginAPI(APIView):
    @csrf_exempt
    def post(self,request,*args,**kwargs):
        if request.method == "POST":
            obj=request.data
            print(obj)
            user_name=obj['mail']
            password=str(obj['pwd'])
            try:
                obj2=user_registartion.objects.filter(email=user_name,password=password).exists()
                print(obj2)
                if obj2:
                    role=user_registartion.objects.filter(email=user_name).values()
                    return Response({'userdata':role,})
                # return render(request,'dashboard.html',{'user_name':user_name})
                else:
                    return Response("User not found", status=status.HTTP_400_BAD_REQUEST)
            except user_registartion.DoesNotExist:
                return Response("User not found", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Method not allowed  ",status=status.HTTP_405_METHOD_NOT_ALLOWED) 
            
class LogoutAPIView(APIView):
    @csrf_exempt
    def out(request):
        logout(request)
        return HttpResponse('logout')
               
class RegistartionAPIView(APIView):
    @csrf_exempt
    def post(self, request,*args,**kwargs):
        print(request.data)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid( ):
            serializer.save()
            return Response({"data":serializer.data})
        else:
            return Response({'errors': serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, format=None):
        if request.method=="GET":
            data_list=user_registartion.objects.all().values()
         
            return Response({"data":data_list})
        else:
            return Response({'errors': serializer.errors},status=status.HTTP_400_BAD_REQUEST)

''' Application fetch data from DatabaseApi that recived post request and send responce ok or 200 status code else return BAD_REQUEST '''
class LoRaDetailsAPI(APIView):
    @csrf_exempt
    def post(self, request,*args,**kwargs):
        print(request.data)
        serializer = LoRaServerSerializer(data=request.data)
        if serializer.is_valid( ):
            serializer.save()
            return Response({"data":serializer.data})
        else:
            return Response({'errors': serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    # def get(self,request,format='json'):
    #     LoRa_server=LoRaServerDetails.objects.values('server_name')
    #     lora_list=[item['server_name'] for item in LoRa_server]
    #     print(lora_list)
    #     return Response(lora_list)





class SiteDetailsAPI(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SiteDetailsSerializer(data=request.data)

        if serializer.is_valid():
            server_name = serializer.validated_data['server_name']
            try:
                server = LoRaServerDetails.objects.get(server_name=server_name)
                site_name = serializer.validated_data['site_name']
                multicast_ids = serializer.validated_data['multicast_id']
                site_owner = serializer.validated_data['site_owner']
                post = site_manager(
                    fk_server_name=server,
                    server_name=server_name,   
                    site_name=site_name,
                    multicast_id=multicast_ids,
                    site_owner=site_owner
                )
                post.save()

                return Response("Maintenance record created successfully", status=status.HTTP_201_CREATED)
            except LoRaServerDetails.DoesNotExist:
                return Response({"error": "LoRaServerDetails not found"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self,request,format='json'):
        site_list=[item['site_name'] for item in site_manager.objects.values('site_name')]
        print(site_list)
        context={
        'site_list':site_list
        }
        return Response(context)


class ServerListDetailsAPI(APIView):
    def get(self, request, sitename, format='json'):
        # Use a list comprehension to create a list of dictionaries
        server_and_multicast = [{'server_name': item['server_name'], 'multicast_add': item['multicast_id']} for item in site_manager.objects.filter(site_name=str(sitename)).values('server_name', 'multicast_id')]

        context = {
            'server_and_multicast': server_and_multicast
        }
        return Response(context)



 
    
class ComplaintAPIView(APIView):
    @csrf_exempt
    def post(self, request,*args,**kwargs):
        print(request.data)

        serializer = DeviceComplaintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data})
        else:
            return Response({'errors': serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        
class MaintenanceAPIView(APIView):
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            obj = request.POST
            device_eui = obj['device_eui']
            comp_number = obj['complaint_number']
             
            print(device_eui)
            try:
                complaint = Complaint.objects.get(complaint_number=comp_number)

            except Complaint.DoesNotExist:
                return Response({"error": "Complaint number not found"}, status=status.HTTP_400_BAD_REQUEST)
            image = request.FILES.get('image')
            post = maintenance()
            post.complaint = complaint
            post.device_eui = obj['device_eui']
            post.date_of_inspection = obj['date_of_inspection']
            post.inspector_name = obj['inspector_name']
            post.device_latitude = obj['device_latitude']
            post.device_longitude = obj['device_longitude']
            post.device_pole_no = obj['device_pole_no']
            post.device_zone = obj['device_zone']
            post.check_choice = obj['check_choice']
            post.cleaned_choice = obj['cleaned_choice']
            post.repaired_choice = obj['repaired_choice']
            post.device_replace = obj['device_replace']
            post.maintenance_status = obj['maintenance_status']
            post.issue_details = obj['issue_details']
            post.complaint_number=obj['complaint_number']
            post.image = image
            post.save()
            return Response("Maintenance record created successfully", status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
       
class DeviceRegisterAPIView(APIView):
    @csrf_exempt
    def post(self, request,*args,**kwargs): 
        if request.method=="POST":
            print(request.data)
            deveui=request.data['dev_eui']
            dbdev=device_register_details.objects.filter(dev_eui=deveui).exists()
            print(dbdev,'HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')
            if dbdev:
                return Response("Device MAC already exists",status=status.HTTP_400_BAD_REQUEST)
            serializer = DeviceRegisterDetailsSerializer(data=request.data)
            if serializer.is_valid( ):
                serializer.save()
                return Response({"data":serializer.data})
            else:
                return Response({'errors': serializer.errors},status=status.HTTP_400_BAD_REQUEST)
   
    @csrf_exempt  
    def get(self, request, format=None):
        device_detail = device_register_details.objects.all().values()
        devicelist = DeviceRegisterDetailsSerializer(device_detail, many=True)
        device_lat = [ i['device_latitude'] for i in device_detail ]
        device_long = [ i['device_longitude'] for i in device_detail]
        context={
        'device_lat':device_lat,
        'device_long':device_long,
        'devicelist':devicelist.data  
        }
        return Response(context)

class GetZoneName(APIView):
    def get(self,request,zonename,format='json'):
        if zonename:
            wards_list=Ward_details.objects.filter(zone_name=zonename).values('ward_name')
            ward_list=[i['ward_name'] for i in wards_list]
            return Response({'ward_list':ward_list})

class ZoneAPI(APIView):
    @csrf_exempt
    def post(self, request,*args,**kwargs):
        print(request.data)
        zone_check= request.data.get('zone_name')
        print(zone_check)
        if Zone_details.objects.filter(zone_name=zone_check).exists():
            return Response('Zone already exists',status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = ZoneSerializer(data=request.data)
            if serializer.is_valid( ):
                serializer.save()
                return Response({"data":serializer.data})
            else:
                return Response({'errors': serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
    @csrf_exempt 
    def get(self, request, format=None):
        if request.method=="GET":
            zone_list=Zone_details.objects.values()
            Zonelist = ZoneSerializer(zone_list, many=True)
            All_Zone_list=Zonelist.data
            zone_name_list=[item['zone_name'] for item in All_Zone_list]
            context={
                'zone_name_list':zone_name_list,
                }
            return Response(context)
        else:
            return Response({'errors': serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse("OKKKK")


class WardAPI(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            ward_name = request.data.get('ward_name')
            zone_name = request.data.get('zone_name')

            # Check if a ward with the same name already exists in the same zone
            ward_exists = Ward_details.objects.filter(ward_name=ward_name, zone_name=zone_name).exists()

            if ward_exists:
                return Response('Ward already exists for this zone', status=status.HTTP_400_BAD_REQUEST)

            serializer = WardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                print('Data saved successfully')
                return Response("Success")
            else:
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Method Not Allowed', status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @csrf_exempt
    def get(self, request, format=None):
        if request.method == "GET":
            ward_list = Ward_details.objects.all()
            ward_data = WardSerializer(ward_list, many=True).data

            All_ward_list = {}

            for ward in ward_data:
                zone_name = ward['zone_name']
                ward_name = ward['ward_name']

                if zone_name not in All_ward_list:
                    All_ward_list[zone_name] = ward_name
                else:
                    All_ward_list[zone_name] += f", {ward_name}"

            return Response(All_ward_list)
        else:
            return Response({'errors': serializer.errors},status=status.HTTP_400_BAD_REQUEST)
      

     

class ComplaintAndMaintenanceAPIView(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        current_date = date.today()
        day_start_time = datetime.combine(current_date, datetime.min.time())
        day_end_time = datetime.combine(current_date, datetime.max.time())

        comlaint_detail = Complaint.objects.filter(date_of_complaint__range=(day_start_time,day_end_time)).values()
        comlaint_count=len(comlaint_detail)

        # comlaintdetail = DeviceComplaintSerializer(comlaint_detail, many=True)

        total_resolved = maintenance.objects.filter(date_of_inspection__range=(day_start_time,day_end_time),maintenance_status='success').values()
        total_resolved_count=len(total_resolved)
       
        resolved_complaints_list = list(total_resolved)

        resolved_ids = maintenance.objects.values_list('complaint_number', flat=True).filter(date_of_inspection__range=(day_start_time,day_end_time),maintenance_status='success')
        print(resolved_ids,'GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG')
        complaint_detail = Complaint.objects.exclude(complaint_number__in=resolved_ids).filter(date_of_complaint__range=(day_start_time,day_end_time)).values()
        print(complaint_detail,'complaint_detailcomplaint_detailcomplaint_detailcomplaint_detailcomplaint_detail')
        open_complaints_count=comlaint_count-total_resolved_count

        open_complaints = complaint_detail.exclude(device_eui__in=resolved_ids)

        # Fetch latitude and longitude for each device_eui
        device_euis = [complaint['device_eui'] for complaint in open_complaints]
        print(device_euis)
        device_details = device_register_details.objects.filter(dev_eui__in=device_euis).values('dev_eui', 'device_latitude', 'device_longitude')
        print(device_details)
        # Add latitude and longitude to each complaint in open_complaints
        for complaint in open_complaints:
            device_eui = complaint['device_eui']
            device_detail = device_details.filter(dev_eui=device_eui).first()
            complaint['lat'] = device_detail['device_latitude']
            complaint['long'] = device_detail['device_longitude']

        print(open_complaints)
      
        context={
            'total_comlaint_count':comlaint_count,
            'total_resolved_count':total_resolved_count,
            'open_complaints_count':open_complaints_count,
            'total_comlaint_detail':comlaint_detail,
            'resolved_complaints_list':resolved_complaints_list,
            'open_complaints':open_complaints,

        }
        return Response(context)
class CustomizeComplaintDetailsAPIView(APIView):
    @csrf_exempt
    def get(self, request,sdate,edate, format=None):
        sdate = datetime.strptime(sdate, '%Y-%m-%d').date()
        edate = datetime.strptime(edate, '%Y-%m-%d').date()
        day_start_time = datetime.combine(sdate, datetime.min.time())
        day_end_time = datetime.combine(edate, datetime.max.time())
        # complaint_detail = Complaint.objects.filter(date_of_complaint__range=(sdate,edate)).values()
        # serializer = DeviceComplaintSerializer(complaint_detail, many=True)
        # finaldata=serializer.data
        # total_resolved = maintenance.objects.filter(date_of_inspection__range=(day_start_time,day_end_time),maintenance_status='success').values()
        # context={
        #         'complaint_details':complaint_detail,
        #         'total_resolved':list(total_resolved),
        #         }

         

        comlaint_detail = Complaint.objects.filter(date_of_complaint__range=(day_start_time,day_end_time)).values()
        

        total_resolved = maintenance.objects.filter(date_of_inspection__range=(day_start_time,day_end_time),maintenance_status='success').values()
       
       
        resolved_complaints_list = list(total_resolved)

        resolved_ids = maintenance.objects.values_list('complaint_number', flat=True).filter(date_of_inspection__range=(day_start_time,day_end_time),maintenance_status='success')
        
        
        complaint_detail = Complaint.objects.exclude(complaint_number__in=resolved_ids).filter(date_of_complaint__range=(day_start_time,day_end_time)).values()
        
         

        open_complaints = complaint_detail.exclude(device_eui__in=resolved_ids)

        # Fetch latitude and longitude for each device_eui
        device_euis = [complaint['device_eui'] for complaint in open_complaints]
        print(device_euis)
        device_details = device_register_details.objects.filter(dev_eui__in=device_euis).values('dev_eui', 'device_latitude', 'device_longitude')
        print(device_details)
        # Add latitude and longitude to each complaint in open_complaints
        for complaint in open_complaints:
            device_eui = complaint['device_eui']
            device_detail = device_details.filter(dev_eui=device_eui).first()
            complaint['lat'] = device_detail['device_latitude']
            complaint['long'] = device_detail['device_longitude']

        print(open_complaints)
      
        context={
    
            'total_comlaint_detail':comlaint_detail,
            'resolved_complaints_list':resolved_complaints_list,
            'open_complaints':open_complaints,

        }
        return Response(context)





class DashboardDataDetailsAPIView(APIView):

    @csrf_exempt
    def get(self, request, format=None):
        current_date = date.today()
    
        day_start_time = datetime.combine(current_date, datetime.min.time())
        day_end_time = datetime.combine(current_date, datetime.max.time())

        previous_week_start = current_date - timedelta(days=7)
        
        previous_week_start_time = datetime.combine(previous_week_start, datetime.min.time())
       
        current_date_end_time = datetime.combine(current_date, datetime.max.time())
       
        #Total device count 
        total_devices_count = device_register_details.objects.values('dev_eui').distinct().count()
        total_on_devices = payloaddata.objects.filter(time_stamp__range=(day_start_time,day_end_time),relay_status__icontains='ON').values('devEUI').distinct().count()
        total_off_devices = payloaddata.objects.filter(time_stamp__range=(day_start_time,day_end_time),relay_status__icontains='OFF').values('devEUI').distinct().count()
        zone_count = Zone_details.objects.values('zone_name').count()
        print()
        ward_count = Ward_details.objects.count()

        Power_fail=payloaddata.objects.filter(time_stamp__range=(day_start_time,day_end_time),power_grid_fail__icontains='Yes').values('devEUI').distinct().count()
        lamp_fali=payloaddata.objects.filter(time_stamp__range=(day_start_time,day_end_time),lamp_fali__icontains='Yes').values('devEUI').distinct().count()
        luc_withmeter_detail=payloaddata.objects.filter(time_stamp__range=(day_start_time,day_end_time),luc_detail__icontains='WithMeter').values('devEUI').distinct().count()
        luc_withoutmeter_detail=payloaddata.objects.filter(time_stamp__range=(day_start_time,day_end_time),luc_detail__icontains='WithOutMeter').values('devEUI').distinct().count()
        relay_status=payloaddata.objects.filter(time_stamp__range=(day_start_time,day_end_time),relay_status__icontains='ON').values('devEUI').distinct().count()
        total_complaints_count = Complaint.objects.filter(date_of_complaint__range=(day_start_time,day_end_time)).count()
        total_resolved_count = maintenance.objects.filter(date_of_inspection__range=(day_start_time,day_end_time),maintenance_status='success').count()
        open_complaints_count=total_complaints_count-total_resolved_count
        
        kwh_used_in_day = payload_power_mst.objects.filter(date=current_date).aggregate(total_power_consume=Sum('power_consume'))
        power_consume_daily = kwh_used_in_day['total_power_consume'] or 0
        power_consume_daily = round(power_consume_daily, 2)

        power_save_in_day = payload_power_mst.objects.filter(date=current_date).aggregate(total_power_save=Sum('power_save'))

        power_save_daily = power_save_in_day['total_power_save'] or 0
        power_save_daily=round(power_save_daily,2)

        all_dates = [previous_week_start + timedelta(days=i) for i in range(8)]

        kwh_used_week = payload_power_mst.objects.filter(date__range=[previous_week_start_time,current_date_end_time]).values('date','power_consume','power_save') 
        serializer=PayloadMstSerializer(kwh_used_week,many=True)
        weekly_list=serializer.data
        # weekly_power_consume_list = {item['date']: round(float(item['power_consume']),2) for item in weekly_list}
        # weekly_power_consume_list=dict(sorted(weekly_power_consume_list.items()))
        
        # weekly_power_save_list = {item['date']: round(float(item['power_save']),2) for item in weekly_list}
        # weekly_power_save_list=dict(sorted(weekly_power_save_list.items()))

        formatted_dates = [date.strftime('%Y-%m-%d') for date in all_dates]

        # Initialize dictionaries for power consume and power save
        weekly_power_consume_list = {date: 0.0 for date in formatted_dates}
        weekly_power_save_list = {date: 0.0 for date in formatted_dates}

        # Now, update the dictionaries with actual data
        for item in weekly_list:
            date_str = item['date']

            if item is not None:
                if item.get('power_consume') is not None:
                    weekly_power_consume_list[date_str] = round(float(item['power_consume']), 2)
                else:
                    weekly_power_consume_list[date_str] = 0
            else:
                weekly_power_consume_list[date_str] = 0
                
            if item is not None:
                if item.get('power_save') is not None:
                    weekly_power_save_list[date_str] = round(float(item['power_save']), 2)
                else:
                    weekly_power_save_list[date_str] = 0
            else:
                weekly_power_save_list[date_str] = 0
             

        # Sort the dictionaries by date
        weekly_power_consume_list = dict(sorted(weekly_power_consume_list.items()))
        weekly_power_save_list = dict(sorted(weekly_power_save_list.items()))

        # Print the updated dictionaries
        print("weekly_power_consume_list:", weekly_power_consume_list)
        print("weekly_power_save_list:", weekly_power_save_list)


         
        zone_filters=list(Zone_details.objects.values_list('zone_name'))
        zone_on_off_counts = {}

        for zone_filter in zone_filters:
            zone_name = zone_filter[0]  # Access the first element of the tuple
            
            zone_data = device_register_details.objects.filter(device_zone=zone_name)
            serializer = DeviceRegisterDetailsSerializer(zone_data, many=True)
            zone_list = serializer.data
            # zone_count = len(zone_list)

            zone_deveui = list({item['dev_eui'] for item in zone_list})
            zone_deveui_count = len(zone_deveui)
            
            on_device_count = payloaddata.objects.filter(time_stamp__range=(day_start_time, day_end_time), relay_status__icontains='ON', devEUI__in=zone_deveui).count()
            off_device_count = zone_deveui_count - on_device_count

            zone_on_off_counts[zone_name] = {
                'total_device': zone_deveui_count,
                'on_device': on_device_count,
                'off_device': off_device_count
            }


        context = {
        'total_devices_count':total_devices_count,
        'total_on_devices':total_on_devices,
        'total_off_devices':total_off_devices,
        'zone_count':zone_count,
        'ward_count':ward_count,

        'Power_fail':Power_fail,
        'lamp_fali':lamp_fali,
        'luc_withmeter_detail':luc_withmeter_detail,
        'luc_withoutmeter_detail':luc_withoutmeter_detail,
        'relay_status':relay_status,
        'total_complaints_count':total_complaints_count,
        'total_resolved_count':total_resolved_count,
        'open_complaints_count':open_complaints_count,
        'power_consume_daily':power_consume_daily,
        'power_save_daily':power_save_daily,
        'weekly_power_consume_list':weekly_power_consume_list,
        'weekly_power_save_list':weekly_power_save_list,
        'zone_on_off_counts':zone_on_off_counts,

        }
        return Response(context)


    def post(self, request,*args,**kwargs):
        if request.method=="POST":
            try:
                obj=request.data
                print(obj)
                get_deveui=obj['devui']

                lat_long=device_register_details.objects.filter(dev_eui=get_deveui).values()
                lat_long_lat = [(i['device_latitude'],i['device_longitude']) for i in lat_long]
                

                context={
                'lat_long_lat':lat_long_lat,
                }
                return Response(context)
            except lat_long_lat.DoesNotExist:
                    return Response({"error": "Device Eui not found"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
 


class CustomPowerSaveAndConsumeAPIView(APIView):
    def get(self, request, sdate, edate):
        sdate = datetime.strptime(sdate, '%Y-%m-%d').date()
        edate = datetime.strptime(edate, '%Y-%m-%d').date()
        day_start_time = datetime.combine(sdate, datetime.min.time())
        day_end_time = datetime.combine(edate, datetime.max.time())

        # Aggregate power consumption and savings for all devices for each date in the specified date range
        aggregated_data = (
            payload_power_mst.objects
            .filter(date__range=(day_start_time, day_end_time))
            .values('date')
            .annotate(total_power_consume=Sum('power_consume'), total_power_save=Sum('power_save'))
            .order_by('date')
        )

        # Convert the result to a list of dictionaries
        aggregated_data_list = list(aggregated_data)

        # Create a dictionary to store the aggregated data with date as the key
        aggregated_data_dict = {str(item['date']): {
            'total_power_consume': round(float(item['total_power_consume'] or 0), 2),
            'total_power_save': round(float(item['total_power_save'] or 0), 2)
        } for item in aggregated_data_list}

        # Create a list of all dates in the date range
        all_dates = [sdate + timedelta(days=i) for i in range((edate - sdate).days + 1)]

        # Populate dictionaries with actual data
        custom_power_consume_list = {str(date): aggregated_data_dict.get(str(date), {'total_power_consume': 0})['total_power_consume'] for date in all_dates}
        custom_power_save_list = {str(date): aggregated_data_dict.get(str(date), {'total_power_save': 0})['total_power_save'] for date in all_dates}

        context = {
            'custom_power_consume_list': custom_power_consume_list,
            'custom_power_save_list': custom_power_save_list,
        }
        return Response(context)

class MonthlyDashboardDataDetailsAPIView(APIView):
    @csrf_exempt
    def get(self, request, month, format='json'):
        month_datetime = datetime.strptime(month, '%Y-%m-%d')
        month_name = month_datetime.month

        print(month_name,"MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")

        current_date = date.today()
        year = date.today().year

        month_wise_count = {}
        month_start_time = datetime(year, month_name, 1)
        print(month_start_time)
        _, last_day = calendar.monthrange(year, month_name)
        month_end_time = datetime(year, month_name, last_day, 23, 59, 59)

        print(month_end_time)

        day_start_time = datetime.combine(current_date, datetime.min.time())
        day_end_time = datetime.combine(current_date, datetime.max.time())

        previous_week_start = current_date - timedelta(days=7)
        previous_week_start_time = datetime.combine(previous_week_start, datetime.min.time())
        current_date_end_time = datetime.combine(current_date, datetime.max.time())

        # Total device count
        total_devices_count = device_register_details.objects.values('dev_eui').distinct().count()
        total_on_devices = payloaddata.objects.filter(time_stamp__range=(day_start_time, day_end_time), relay_status__icontains='ON').values('devEUI').distinct().count()
        total_off_devices = payloaddata.objects.filter(time_stamp__range=(day_start_time, day_end_time), relay_status__icontains='OFF').values('devEUI').distinct().count()
        zone_count = Zone_details.objects.count()
        ward_count = Ward_details.objects.count()


        monthly_Power_fail=payloaddata.objects.filter(time_stamp__range=(month_start_time,month_end_time),power_grid_fail__icontains='Yes').values('devEUI').distinct().count()
        monthly_lamp_fali=payloaddata.objects.filter(time_stamp__range=(month_start_time,month_end_time),lamp_fali__icontains='Yes').values('devEUI').distinct().count()
        monthly_luc_withmeter_detail=payloaddata.objects.filter(time_stamp__range=(month_start_time,month_end_time),luc_detail__icontains='WithMeter').values('devEUI').distinct().count()
        monthly_luc_withoutmeter_detail=payloaddata.objects.filter(time_stamp__range=(month_start_time,month_end_time),luc_detail__icontains='WithOutMeter').values('devEUI').distinct().count()
        monthly_relay_status=payloaddata.objects.filter(time_stamp__range=(month_start_time,month_end_time),relay_status__icontains='ON').values('devEUI').distinct().count()

 
        total_complaints_count = Complaint.objects.filter(date_of_complaint__range=(month_start_time, month_end_time)).count()
        total_resolved_count = maintenance.objects.filter(date_of_inspection__range=(month_start_time, month_end_time), maintenance_status='success').count()
        open_complaints_count = total_complaints_count - total_resolved_count

        kwh_used_in_day = payload_power_mst.objects.filter(date__range=(month_start_time,month_end_time)).aggregate(total_power_consume=Sum('power_consume'))
        power_consume_daily = kwh_used_in_day['total_power_consume'] or 0
        power_consume_daily = round(power_consume_daily, 2)
        power_save_in_day = payload_power_mst.objects.filter(date__range=(month_start_time,month_end_time)).aggregate(total_power_save=Sum('power_save'))
        power_save_daily = power_save_in_day['total_power_save'] or 0
        power_save_daily = round(power_save_daily, 2)
        zone_filters = list(Zone_details.objects.values_list('zone_name', flat=True))

        zone_on_off_counts = {}

        for zone_filter in zone_filters:
            zone_data = device_register_details.objects.filter(device_zone=zone_filter)
            serializer = DeviceRegisterDetailsSerializer(zone_data, many=True)
            zone_list = serializer.data
            zone_count = len(zone_list)

            zone_deveui = list({item['dev_eui'] for item in zone_list})
            zone_deveui_count = len(zone_deveui)

            on_device_count = payloaddata.objects.filter(time_stamp__range=(day_start_time, day_end_time), relay_status__icontains='ON', devEUI__in=zone_deveui).count()
            off_device_count = zone_deveui_count - on_device_count

            zone_on_off_counts[zone_filter] = {
                'total_device': zone_deveui_count,
                'on_device': on_device_count,
                'off_device': off_device_count
            }

        all_dates = [month_start_time + timedelta(days=i) for i in range((month_end_time - month_start_time).days + 1)]
        weekly_power_consume_dict = {}
        weekly_power_save_dict = {}
        aggregated_data = (
            payload_power_mst.objects
            .filter(date__range=(month_start_time, month_end_time))
            .values('date')
            .annotate(total_power_consume=Sum('power_consume'), total_power_save=Sum('power_save'))
            .order_by('date')
        )
        aggregated_data_list = list(aggregated_data)
        print(aggregated_data_list)
        aggregated_data_dict = {item['date']: {
            'total_power_consume': round(float(item['total_power_consume'] or 0), 2),
            'total_power_save': round(float(item['total_power_save'] or 0), 2)
        } for item in aggregated_data_list}

        print(aggregated_data_dict)

        # Populate dictionaries with actual data

        for dates in all_dates:
            date_str = str(dates.date())
            date_key = dates.date()  # Keep the original date for comparison
            print(date_key)
            if date_key in aggregated_data_dict:
                weekly_power_consume_dict[date_str] = aggregated_data_dict[date_key]['total_power_consume']
                weekly_power_save_dict[date_str] = aggregated_data_dict[date_key]['total_power_save']
            else:
                weekly_power_consume_dict[date_str] = 0
                weekly_power_save_dict[date_str] = 0





     

        context = {
            'monthly_devices_count': total_devices_count,
            'monthly_on_devices': total_on_devices,
            'monthly_off_devices': total_off_devices,
            'monthly_zone_count': zone_count,
            'monthly_ward_count': ward_count,
            'monthly_Power_fail':monthly_Power_fail,
            'monthly_lamp_fali':monthly_lamp_fali,
            'monthly_luc_withmeter_detail':monthly_luc_withmeter_detail,
            'monthly_luc_withoutmeter_detail':monthly_luc_withoutmeter_detail,
            'monthly_relay_status':monthly_relay_status,
            'monthly_complaints_count': total_complaints_count,
            'monthly_resolved_count': total_resolved_count,
            'monthly_open_complaints_count': open_complaints_count,

            'monthly_power_consume_daily': power_consume_daily,
            'monthly_power_save_daily': power_save_daily,

            # 'weekly_power_consume_list': weekly_power_consume_list,
            # 'weekly_power_save_list': weekly_power_save_list,

            'zone_on_off_counts': zone_on_off_counts,
            'weekly_power_consume_list':weekly_power_consume_dict,
            'weekly_power_save_list':weekly_power_save_dict
            
        }
        return Response(context)


# class SearchDeviseAPIView(APIView):
#     def get(self, request, deveui, format=None):
#         if deveui is not None:
#             print(deveui)
#             devise_data=device_register_details.objects.filter(dev_eui=deveui).values()
#             serializer_data = DeviceRegisterDetailsSerializer(devise_data, many=True)
#             search_result=serializer_data.data
#             print(search_result,'hhhhhhhhhhhhhhhhhhhhhhhhhh')

#             devisedata=payloaddata.objects.filter(devEUI=deveui).values()
#             print(devisedata)
            
#             fun_lamp=[ i['lamp_fali'] for i in devisedata] #  current lamp status and  on/ off count
#             print(fun_lamp)
#             current_lamp=fun_lamp[-1]
#             lamp_fali_yes=[]
#             lamp_fali_no=[]
#             for i in fun_lamp:
#                 if i=='1':
#                     lamp_fali_yes.append(i)
#                 else:
#                     lamp_fali_no.append(i)


#             count_lamp_fali_yes=len(lamp_fali_yes)  # final output


#             fun_power_status=[ i['power_grid_fail'] for i in devisedata] # current power status and power fail yes/no status
#             current_power_status=fun_power_status[::-1]
#             power_fail_yes=[]
#             for i in fun_power_status:
#                 if i=='1':
#                     power_fail_yes.append(i)
#             count_power_fail_yes=len(power_fail_yes)  #################final output


#             fun_relay=[ i['relay_status'] for i in devisedata ]  ##### current relay status and relay_status on/off status
#             print(fun_relay,"RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
#             current_relay_status=fun_relay[-1]
#             relay_on_yes=[]
#             for i in fun_relay:
#                 if i=='1':
#                     relay_on_yes.append(i)
#             count_relay_on_yes=len(relay_on_yes)  #################final output


#             fun_lat = [ i['latitude'] for i in devisedata ]
#             current_lat=fun_lat[-1]

#             fun_long = [ i['longitude'] for i in devisedata]
#             current_long=fun_long[-1]



#             kwh_used_in_day = payload_power_mst.objects.filter(device_eui=deveui).aggregate(total_power_consume=Sum('power_consume'))
#             power_consume_daily = kwh_used_in_day['total_power_consume'] or 0
#             power_consume_daily = round(power_consume_daily, 2)
#             power_save_in_day = payload_power_mst.objects.filter(device_eui=deveui).aggregate(total_power_save=Sum('power_save'))
#             power_save_daily = power_save_in_day['total_power_save'] or 0
#             power_save_daily = round(power_save_daily, 2)



#             fun_voltage = [ i['meter_voltage'] for i in devisedata]
#             current_voltage=fun_voltage[-1]

#             context={
#              'search_result':search_result,
#              'devisedata':devisedata,
#              'current_lamp':current_lamp,
#              'lamp_fali_yes':lamp_fali_yes,
#              'lamp_fali_no':lamp_fali_no,
#              'count_lamp_fali_yes':count_lamp_fali_yes,
#              'current_power_status':current_power_status,
#              'count_power_fail_yes':count_power_fail_yes,
#              'current_relay_status':current_relay_status,
#              'count_relay_on_yes':count_relay_on_yes,
#              'current_lat':current_lat,
#              'current_long':current_long,
#              'consume_power':power_consume_daily,
#              'save_power':power_save_daily,
#              'current_voltage':current_voltage,
#              }
#             return Response(context)

 
from datetime import datetime, timezone
import pytz
# day_start_time = datetime.combine(current_date, datetime.min.time(), tzinfo=timezone.utc)

# class SearchDeviseAPIView(APIView):
#     def get(self, request, deveui, format=None):
#         if deveui is not None:
#             print(deveui)
#             current_date=date.today()
#             day_start_time = datetime.combine(current_date, datetime.min.time())
#             day_end_time = datetime.combine(current_date, datetime.max.time())
#             devise_data = device_register_details.objects.filter(dev_eui=deveui).values()
#             serializer_data = DeviceRegisterDetailsSerializer(devise_data, many=True)
#             search_result = serializer_data.data
#             print(search_result, 'hhhhhhhhhhhhhhhhhhhhhhhhhh')

#             devisedata = payloaddata.objects.filter(devEUI=deveui,time_stamp__range=(day_start_time,day_end_time)).values().last()
#             print(devisedata)

#             fun_lamp = [i['lamp_fali'] for i in devisedata]  # current lamp status and on/off count
#             print(fun_lamp)
#             lamp_fali_yes = []
#             lamp_fali_no = []
#             if fun_lamp:
#                 current_lamp = fun_lamp[-1]
#                 for i in fun_lamp:
#                     if i == '1':
#                         lamp_fali_yes.append(i)
#                     else:
#                         lamp_fali_no.append(i)

#                 count_lamp_fali_yes = len(lamp_fali_yes)  # final output
#             else:
#                 current_lamp = None
#                 count_lamp_fali_yes = 0

#             fun_power_status = [i['power_grid_fail'] for i in devisedata]  # current power status and power fail yes/no status
#             current_power_status = fun_power_status[::-1]
#             power_fail_yes = []
#             for i in fun_power_status:
#                 if i == '1':
#                     power_fail_yes.append(i)
#             count_power_fail_yes = len(power_fail_yes)  #################final output

#             fun_relay = [i['relay_status'] for i in devisedata]  ##### current relay status and relay_status on/off status
#             print(fun_relay, "RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
            
#             if fun_relay:
#                 current_relay_status = fun_relay[-1]
#                 relay_on_yes = []
#                 for i in fun_relay:
#                     if i == '1':
#                         relay_on_yes.append(i)
#                 count_relay_on_yes = len(relay_on_yes)  #################final output
#             else:
#                 current_relay_status = None
#                 count_relay_on_yes = 0

#             fun_lat = [i['latitude'] for i in devisedata]
#             if fun_lat:
#                 current_lat = fun_lat[-1]
#             else:
#                 current_lat = None  # or some default value

#             fun_long = [i['longitude'] for i in devisedata]
#             if fun_long:
#                 current_long = fun_long[-1]
#             else:
#                 current_long = None  # or some default value
            

#             kwh_used_in_day = payload_power_mst.objects.filter(device_eui=deveui).aggregate(total_power_consume=Sum('power_consume'))
#             power_consume_daily = kwh_used_in_day['total_power_consume'] or 0
#             power_consume_daily = round(power_consume_daily, 2)
#             power_save_in_day = payload_power_mst.objects.filter(device_eui=deveui).aggregate(total_power_save=Sum('power_save'))
#             power_save_daily = power_save_in_day['total_power_save'] or 0
#             power_save_daily = round(power_save_daily, 2)

#             fun_voltage = [i['meter_voltage'] for i in devisedata]
#             if fun_voltage:
#                 current_voltage = fun_long[-1]
#             else:
#                 current_voltage = 'NA'
             

#             context = {
#                 'search_result': search_result,
#                 'devisedata': devisedata,
#                 'current_lamp': current_lamp,
#                 'lamp_fali_yes': lamp_fali_yes,
#                 'lamp_fali_no': lamp_fali_no,
#                 'count_lamp_fali_yes': count_lamp_fali_yes,
#                 'current_power_status': current_power_status,
#                 'count_power_fail_yes': count_power_fail_yes,
#                 'current_relay_status': current_relay_status,
#                 'count_relay_on_yes': count_relay_on_yes,
#                 'current_lat': current_lat,
#                 'current_long': current_long,
#                 'consume_power': power_consume_daily,
#                 'save_power': power_save_daily,
#                 'current_voltage': current_voltage,
#             }
#             return Response(context)
#         else:
#             return HttpResponse("Invalid deveui parameter.")

class SearchDeviseAPIView(APIView):
    def get(self, request, deveui, format=None):
        if deveui is not None:
            print(deveui)
            current_date = date.today()
            day_start_time = datetime.combine(current_date, datetime.min.time())
            day_end_time = datetime.combine(current_date, datetime.max.time()) 
            devise_data = device_register_details.objects.filter(dev_eui=deveui).values()
            if devise_data is not None:
                serializer_data = DeviceRegisterDetailsSerializer(devise_data, many=True)
                search_result = serializer_data.data
                print(search_result, 'hhhhhhhhhhhhhhhhhhhhhhhhhh')

                devisedata = payloaddata.objects.filter(devEUI=deveui, time_stamp__range=(day_start_time, day_end_time)).values().last()
                print(devisedata)

            
                if devisedata is not None:
                    current_lamp = devisedata.get('lamp_fali')
                    current_power_status = devisedata.get('power_grid_fail')
                    current_relay_status = devisedata.get('relay_status')
                    current_lat = devisedata.get('latitude')
                    current_long = devisedata.get('longitude')
                    current_voltage = devisedata.get('meter_voltage')
                else:
                    current_lamp = None
                    current_power_status=None
                    current_relay_status=None
                    current_lat=None
                    current_long=None
                    current_voltage=None
                

                current_values = {
                'current_lamp': current_lamp,
                'current_power_status': current_power_status,
                'current_relay_status': current_relay_status,
                'current_lat': current_lat,
                'current_long': current_long,
                'current_voltage': current_voltage,
                }

                power_data = payload_power_mst.objects.filter(device_eui=deveui)
                agg_data = power_data.aggregate(
                    total_power_consume=Sum('power_consume'),
                    total_power_save=Sum('power_save')
                )

                total_power_consume = round(agg_data['total_power_consume'] or 0, 2)
                total_power_save = round(agg_data['total_power_save'] or 0, 2)
                grid_fail_count = payloaddata.objects.filter(devEUI=deveui, power_grid_fail='YES').count()
                lamp_fail_count = payloaddata.objects.filter(devEUI=deveui, lamp_fali='YES').count()

                print("Grid Fail Count:", grid_fail_count)
                print("Lamp Fail Count:", lamp_fail_count)

               
                
                context = {
                    'search_result': search_result,
                    'devisedata': devisedata,
                    'current_values':current_values,
                    'consume_power': total_power_consume,
                    'save_power': total_power_save,
                    'grid_fail_count':grid_fail_count,
                    'lamp_fail_count':lamp_fail_count,
                }
                return Response(context)
            else:
                return HttpResponse("Invalid deveui parameter.")
        else:
            return HttpResponse("Invalid deveui parameter.")

 

  ######################################### Zone View ########################## 

class SearchZoneViewAPI(APIView):
    @csrf_exempt
    def get(self, request, zonetype, format=None):
        print(zonetype)
        if zonetype is not None:
            try:
                current_date = date.today()
                day_start_time = datetime.combine(current_date, datetime.min.time())
                day_end_time = datetime.combine(current_date, datetime.max.time())

                total_zone_device = device_register_details.objects.filter(device_zone=zonetype).values()
                total_zone_device_count=total_zone_device.count()

                total_zone_on_decice_list = payload_power_mst.objects.filter(date__range=(day_start_time,day_end_time),zone_name=zonetype,device_on_off__contains='ON').values()
                total_zone_on_decice_count=total_zone_on_decice_list.count()

                total_zone_off_decice_list = payload_power_mst.objects.filter(date__range=(day_start_time,day_end_time),zone_name=zonetype,device_on_off__contains='OFF').values()
                total_off_devices_count=total_zone_off_decice_list.count()

                zone_power_consume = payload_power_mst.objects.filter(date__range=(day_start_time, day_end_time), zone_name=zonetype).values('zone_name').annotate(power_consume_sum=Sum('power_consume'))
                try:
                    power_consume_sum = 0  # Initialize power_consume_sum before the loop
                    for row in zone_power_consume:
                        power_consume_sum += row['power_consume_sum'] or 0  # Use += to add the value

                    power_save_sum = 0  # Initialize power_save_sum before the loop
                    zone_power_save = payload_power_mst.objects.filter(date__range=(day_start_time, day_end_time), zone_name=zonetype).values('zone_name').annotate(power_save_sum=Sum('power_save'))
                    for row in zone_power_save:
                        power_save_sum += row['power_save_sum'] or 0  # Use += to add the value
                        print(power_save_sum)

                except DoesNotExist:
                    return Response({"error": "Device Eui not found"}, status=status.HTTP_400_BAD_REQUEST)



                context = {
                    'total_zone_device_count':total_zone_device_count,
                    'total_zone_on_decice_count': total_zone_on_decice_count,
                    'total_off_devices_count':total_off_devices_count,
                    'zone_power_consume':power_consume_sum,
                    'zone_power_save':power_save_sum,
                    'total_zone_device':total_zone_device,
                    'total_zone_on_decice_list':total_zone_on_decice_list,
                    'total_zone_off_decice_list':total_zone_off_decice_list,

                }
                return Response(context)
            except payload_power_mst.DoesNotExist:
                return Response({"error": "Device not found"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Invalid student_Deveui parameter"}, status=status.HTTP_400_BAD_REQUEST)



class SearchMapViewAPI(APIView):
    @csrf_exempt
    def get(self, request, zonetype,wardname,format=None):
        print(zonetype)
        print(wardname)

        if zonetype and wardname is not None:
            try:
                all_dev_details=device_register_details.objects.filter(device_zone=zonetype ,device_ward=wardname).values('dev_eui','device_zone','device_ward','device_latitude','device_longitude')
            except DoesNotExist:
                return Response({"error": "Device Eui not found"}, status=status.HTTP_400_BAD_REQUEST)
            context = {
                'all_dev_details':all_dev_details,}
            return Response(context)
             
        else:
            return Response({"error": "Invalid student_Deveui parameter"}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def create_bulk(file_path):
    df =pd.read_csv(file_path,delimiter=',')
    print(df.values)
    list_of_csv=[list(row) for row in df.values]
    for l in list_of_csv:
        deveui=l[0]
        dbdev=device_register_details.objects.filter(dev_eui=deveui).exists()
        print(dbdev)
        if dbdev:
            print("please enter correct deveui")
        else:
            device_register_details.objects.create(
                dev_eui=l[0],
                device_zone=l[1],
                device_ward=l[2],
                pol_number=l[3], 
                device_watt=l[4],
                device_type=l[5],
                device_latitude=l[6],
                device_longitude=l[7],
                dev_reg_date=l[8]
                )

@csrf_exempt           
@api_view(['GET', 'POST'])
def bulk_csv(request):
    if request.method=="POST":
        file=request.FILES.get('file')
        print(file)
        obj=BulkFile.objects.create(file=file)
        create_bulk(obj.file)
    return HttpResponse("File Uploaded")

class DeviceDetailsAPIView(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        # Get the latest device details for the given time range
        current_date = date.today()
        day_start_time = datetime.combine(current_date, datetime.min.time())
        day_end_time = datetime.combine(current_date, datetime.max.time())

        # Retrieve all data within the time range
        all_device_data = payloaddata.objects.filter(time_stamp__range=(day_start_time, day_end_time))

        # Initialize dictionaries to store the latest ON and OFF devices
        latest_ON_device = {}
        latest_OFF_device = {}

        # Iterate through the data to find the latest records for each devEUI
        for data in all_device_data:
            devEUI = data.devEUI
            relay_status = data.relay_status
            time_stamp = data.time_stamp

            if relay_status == 'ON':
                # Check if it's the latest ON record for this devEUI
                if devEUI not in latest_ON_device or time_stamp > latest_ON_device[devEUI].time_stamp:
                    latest_ON_device[devEUI] = data
            elif relay_status == 'OFF':
                # Check if it's the latest OFF record for this devEUI
                if devEUI not in latest_OFF_device or time_stamp > latest_OFF_device[devEUI].time_stamp:
                    latest_OFF_device[devEUI] = data

        # Convert the dictionaries to lists of values
        ON_device = list(latest_ON_device.values())
        OFF_device = list(latest_OFF_device.values())

        # Serialize the data
        serializer = PayloadSerializer(all_device_data, many=True)

        context = {
            'all_device_list': serializer.data,
            'ON_device': serializer.data if ON_device else [],
            'OFF_device': serializer.data if OFF_device else [],
        }

        return Response(context)







class CustomizeDeviceDetailsAPIView(APIView):
    @csrf_exempt
    def get(self, request,sdate,edate, format=None):
        device_detail = payloaddata.objects.filter(time_stamp__range=(sdate,edate)).values().distinct()
        serializer = PayloadSerializer(device_detail, many=True)
        finaldata=serializer.data
        context={
                'all_device_list':finaldata,}
        return Response(context)

class UpdateDeviceAPIView(APIView):
    def get_object(self, deveui):
        try:
            return device_register_details.objects.get(dev_eui=deveui)
        except device_register_details.DoesNotExist:
            return HttpResponse("please enter correct details ")

    def get(self, request, deveui, format=None):
        snippet = self.get_object(deveui)
        serializer = DeviceRegisterDetailsSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, deveui, format=None):
        updatedata = self.get_object(deveui)
        serializer = DeviceRegisterDetailsSerializer(updatedata, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, deveui, format=None):
        updatedevice = self.get_object(deveui)
        serializer = DeviceRegisterDetailsSerializer(updatedevice,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, deveui, format=None):
        updatedata = self.get_object(deveui)
        if isinstance(updatedata, HttpResponse):
            return updatedata
        updatedata.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 


class MonthlyDevicecount(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        if request.method=="POST":
            obj=request.data
            print(obj)
            month_dash=obj['month']
            
            todays_date = date.today()
            c=date.today().month
            print(c)
            print(todays_date)

            Current_year=todays_date.year
            Current_month=todays_date.month

            print(Current_month)
            first_date = datetime(Current_year, month_dash, 1)
            print(first_date,'GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG')

            if Current_month == 12:
                last_date = datetime(Current_year, month_dash, 31)
                print(last_date,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
            else:
                last_date = datetime(Current_year, month_dash + 1, 1) + relativedelta(days=-1)
                print(last_date,"EEEEEEEEEEEEELLLLLLLLLLLLLLLLEEEEEEEEEEEEESSSSSSSSSSSSSSEEEEEEE")
             
            ################# Monthly wise ################
            ##################Total device count ################

            
            monthly_device_detail=device_register_details.objects.values('dev_eui').distinct().filter(dev_reg_date__gte=first_date,dev_reg_date__lte= last_date)
            monthly_total_device_detail=len(monthly_device_detail)
            print(monthly_device_detail,"LLLLL")

            #########################ON/OFF####################################

            on_off_detail=payloaddata.objects.values('relay_status').distinct().filter(time_stamp__gte=first_date,time_stamp__lte= last_date)
            
            ON_off_list = [ i['relay_status'] for i in on_off_detail]
            on_list=[]
            off_list=[]
            for i in ON_off_list:
                if i=="1":
                    on_list.append(i)
                else:
                    off_list.append(i)

            total_on=len(on_list)
            total_off=len(off_list)

            ######################### power used in month ####################################

            kwh_used=payloaddata.objects.filter(time_stamp__gte=first_date,time_stamp__lte= last_date).values()
            monthly_kwh_used = [ i['meter_kwh'] for i in kwh_used]
            print(monthly_kwh_used,"HHHHHHHHHHHHHHHHHHHHHH")
             
            # monthly_use_power=monthly_kwh_used[::-1]
            print(monthly_kwh_used)
            Monthly_totalkwh=np.diff(monthly_kwh_used)
            print(Monthly_totalkwh)

            total_used_power_monthly=sum(Monthly_totalkwh)

           
            print(monthly_total_device_detail,"LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")




             ######################### power used in month ####################################

            high_per=payloaddata.objects.all().values()

         
            total_hr_high=max[first_slot_dimming,second_slot_dimming,third_slot_dimming,fourth_slot_dimming]

            print(total_hr_high)

            print(monthly_total_device_detail,"LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")

            
            context = {
            'deveui_list':monthly_total_device_detail,
            'total_on':total_on,
            'total_off':total_off,
            'total_used_power_monthly':total_used_power_monthly,
            }
            return Response(context)
            
            context = {
            'deveui_list':monthly_total_device_detail,
            'total_on':total_on,
            'total_off':total_off,
            'total_used_power_monthly':total_used_power_monthly,
            }
            return Response(context)


class AppReportAPI(APIView):
    @csrf_exempt
    def post(self, request,*args,**kwargs):
        if request.method=="POST":
            obj=request.data
            print(obj)
            start_date=obj['start']
            print(start_date)
            end_date=obj['end']
            print(end_date)
            report_data=maintenance.objects.filter(date_of_inspection__gte=start_date, date_of_inspection__lte=end_date).values('complaint','device_eui','date_of_inspection','inspector_name','device_latitude','device_longitude','device_pole_no','device_zone','check_choice','cleaned_choice','repaired_choice','device_replace','maintenance_status','issue_details')
            print(report_data)
            context={
            'report_data':report_data,
            }
            return Response(context)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class AllDeviceDetailsAPIView(APIView):
    def get(self, request, format=None):
        grid_fail_count = PayloadData.objects.filter(power_grid_fail=1, date_field=date.today()).count()
        lamp_fail_count = PayloadData.objects.filter(lamp_fail=1, date_field=date.today()).count()

        # Retrieve other details for the current date
        lcu_details = PayloadData.objects.filter(date_field=date.today()).values('lcu_details')
        schedule_mode = PayloadData.objects.filter(date_field=date.today()).values('schedule_mode')
        command_action_status = PayloadData.objects.filter(date_field=date.today()).values('command_action_status')
        relay_status = PayloadData.objects.filter(date_field=date.today()).values('relay_status')

        # Create a dictionary with the retrieved data
        data = {
            'grid_fail_count': grid_fail_count,
            'lamp_fail_count': lamp_fail_count,
            'lcu_details': list(lcu_details),
            'schedule_mode': list(schedule_mode),
            'command_action_status': list(command_action_status),
            'relay_status': list(relay_status)
        }

        return JsonResponse(data)
##################################################### zone view Analysis ############################################

class AllZoneAnalysisAPIView(APIView):
    def get(self, request, zonename, ward=None, format='json'):
        # Assuming 'reciver_zone' refers to the received zone field in the model
        devices = payloaddata_mst.objects.filter(reciver_zone=zonename)

        if ward is not None:
            devices = devices.filter(ward=ward)

        on_devices_count = devices.filter(status="on").count()
        off_devices_count = devices.filter(status="off").count()

        result = {
            "on_devices_count": on_devices_count,
            "off_devices_count": off_devices_count
        }

        return JsonResponse(result)

 
######################################################### Power Trend for week month quater, yearly  ##############
class PowerTrendAnalysisAPIView(APIView):
    def get(self, request, trendtype, format='json'):
        if trendtype == "WEEKLY":
            current_day = date.today()
            week_start = current_day - timedelta(days=7)
            week_start_time = datetime.combine(week_start, datetime.min.time())
            week_end_time = datetime.combine(current_day, datetime.max.time())

            all_dates = [week_start_time + timedelta(days=i) for i in range((week_end_time - week_start_time).days + 1)]

            # Initialize dictionaries for power consumption and power saving data
            
            weekly_power_dict = {}

            # Aggregate power consumption and savings for all devices for each date in the specified week range
            aggregated_data = (
                payload_power_mst.objects
                .filter(date__range=(week_start_time, week_end_time))
                .values('date')
                .annotate(total_power_consume=Sum('power_consume'), total_power_save=Sum('power_save'))
                .order_by('date')
            )

            # Convert the result to a list of dictionaries
            aggregated_data_list = list(aggregated_data)

            # Create a dictionary to store the aggregated data with date as the key (date only)
            aggregated_data_dict = {item['date']: {
                'total_power_consume': round(float(item['total_power_consume'] or 0), 2),
                'total_power_save': round(float(item['total_power_save'] or 0), 2)
            } for item in aggregated_data_list}

            # Populate dictionaries with actual data
            for dates in all_dates:
                date_str = str(dates.date())
                date_key = dates.date()  # Keep the original date for comparison
                if date_key in aggregated_data_dict:
                    weekly_power_dict[date_str] = {
                        'power_consume': aggregated_data_dict[date_key]['total_power_consume'],
                        'power_save': aggregated_data_dict[date_key]['total_power_save']
                    }
                else:
                    weekly_power_dict[date_str] = {
                        'power_consume': 0,
                        'power_save': 0
                    }

            context = {
                'weekly_power_dict': weekly_power_dict,
            }

            return Response(context)
 




        elif trendtype == "MONTHLY":
            current_day = date.today()
            current_year = current_day.year
            current_month = current_day.month

            monthly_power_save_consume = {}

            for month in range(1, current_month + 1):
                month_start_time = datetime(current_year, month, 1)
                _, last_day = calendar.monthrange(current_year, month)
                month_end_time = datetime(current_year, month, last_day, 23, 59, 59)

                monthly_data = payload_power_mst.objects.filter(date__range=(month_start_time, month_end_time)).values('date').annotate(
                    monthly_consume=Coalesce(Sum('power_consume', output_field=CharField()), Value(0, output_field=CharField()))
                    ).annotate(
                    monthly_save=Coalesce(Sum('power_save', output_field=CharField()), Value(0, output_field=CharField())))

                for entry in monthly_data:
                    month_name = entry['date'].strftime('%B')
                    power_consume_sum = float(entry['monthly_consume'])
                    power_save_sum = float(entry['monthly_save'])

                    if month_name not in monthly_power_save_consume:
                        monthly_power_save_consume[month_name] = {'power_consume': 0, 'power_save': 0}

                    monthly_power_save_consume[month_name]['power_consume'] += power_consume_sum
                    monthly_power_save_consume[month_name]['power_save'] += power_save_sum

            # Get a sorted list of month names
            sorted_months = sorted(calendar.month_name[1:current_month + 1], key=lambda x: list(calendar.month_name).index(x))

            # Fill in missing months with 0 values
            for month_name in sorted_months:
                if month_name not in monthly_power_save_consume:
                    monthly_power_save_consume[month_name] = {'power_consume': 0, 'power_save': 0}

            context = {'weekly_power_dict':monthly_power_save_consume}
            return Response(context)

        # elif trendtype=="MONTHLY":
        #     current_day = date.today()
        #     current_year = current_day.year
        #     current_month = current_day.month

        #     monthly_power_save_consume = {}

        #     for month in range(1, current_month + 1):
        #         month_start_time = datetime(current_year, month, 1)
        #         _, last_day = calendar.monthrange(current_year, month)
        #         month_end_time = datetime(current_year, month, last_day, 23, 59, 59)

        #         monthly_data = payload_power_mst.objects.filter(date__range=(month_start_time, month_end_time)).values('date').annotate(
        #             monthly_consume=Coalesce(Sum('power_consume', output_field=CharField()), Value(0, output_field=CharField()))
        #         ).annotate(
        #             monthly_save=Coalesce(Sum('power_save', output_field=CharField()), Value(0, output_field=CharField()))
        #         )
        #         for entry in monthly_data:
        #             date_str = entry['date'].strftime('%B')
        #             power_consume_sum = int(entry['monthly_consume'])
        #             power_save_sum = int(entry['monthly_save'])

        #             if date_str not in monthly_power_save_consume:
        #                 monthly_power_save_consume[date_str] = {'power_consume': 0, 'power_save': 0}
        #             monthly_power_save_consume[date_str]['power_consume'] += power_consume_sum
        #             monthly_power_save_consume[date_str]['power_save'] += power_save_sum
        #     context = {'monthly_power_save_consume': monthly_power_save_consume}
        #     return Response(context)
             

        elif trendtype=="QUATERLY":
            current_day = date.today()
            current_year = current_day.year
            current_month = current_day.month

            quaterly_power_save_consume = {}

            quarters = {
                1: 'Q1',
                2: 'Q2',
                3: 'Q3',
                4: 'Q4'
            }

            for quarter in range(1, current_month // 3 + 1):
                start_month = (quarter - 1) * 3 + 1
                end_month = quarter * 3

                quarter_start_time = datetime(current_year, start_month, 1)
                _, last_day = calendar.monthrange(current_year, end_month)
                quarter_end_time = datetime(current_year, end_month, last_day, 23, 59, 59)

                quarterly_data = payload_power_mst.objects.filter(date__range=(quarter_start_time, quarter_end_time)).values('date').annotate(
                    quarterly_consume=Coalesce(Sum('power_consume', output_field=CharField()), Value(0, output_field=CharField()))
                ).annotate(
                    quarterly_save=Coalesce(Sum('power_save', output_field=CharField()), Value(0, output_field=CharField()))
                )

                for entry in quarterly_data:
                    date_str = quarters[quarter]
                    power_consume_sum = float(entry['quarterly_consume'])
                    power_save_sum = float(entry['quarterly_save'])

                    if date_str not in quaterly_power_save_consume:
                        quaterly_power_save_consume[date_str] = {'power_consume': 0, 'power_save': 0}

                    quaterly_power_save_consume[date_str]['power_consume'] += power_consume_sum
                    quaterly_power_save_consume[date_str]['power_save'] += power_save_sum

            context = {'quaterly_power_save_consume': quaterly_power_save_consume}
            return Response(context)
           


        elif trendtype=="YEARLY":
            current_day = date.today()
            current_year = current_day.year
            current_month = current_day.month

            yearly_power_save_consume = {}

            for year in range(current_year, current_year + 5):  # Change the range as per your requirement
                year_start_time = datetime(year, 1, 1)
                year_end_time = datetime(year, 12, 31, 23, 59, 59)

                yearly_data = payload_power_mst.objects.filter(date__range=(year_start_time, year_end_time)).values('date').annotate(
                    yearly_consume=Coalesce(Sum('power_consume', output_field=CharField()), Value(0, output_field=CharField()))
                ).annotate(
                    yearly_save=Coalesce(Sum('power_save', output_field=CharField()), Value(0, output_field=CharField()))
                )

                for entry in yearly_data:
                    date_str = str(year)
                    power_consume_sum = float(entry['yearly_consume'])
                    power_save_sum = float(entry['yearly_save'])

                    if date_str not in yearly_power_save_consume:
                        yearly_power_save_consume[date_str] = {'power_consume': 0, 'power_save': 0}

                    yearly_power_save_consume[date_str]['power_consume'] += power_consume_sum
                    yearly_power_save_consume[date_str]['power_save'] += power_save_sum

            context = {'yearly_power_save_consume': yearly_power_save_consume}
            return Response(context)

           


        else:
            return Response('status',status=status.HTTP_400_BAD_REQUEST)
            
# class Powercount(APIView):
#     @csrf_exempt
#     def get(self, request, format=None):
#         start_time="2023-04-04 00:18:23"
#         end_time="2023-04-05 23:38:17"
#         x=payloaddata.objects.filter(time_stamp__range=[start_time, end_time]).values()
#         used_kwh = [ i['meter_kwh'] for i in x ]
#         copy_kwh=used_kwh[::-1]
#         use_kwh=np.diff(copy_kwh)
#         total_used_power=sum(use_kwh)
#         day_kwh =payloaddata.objects.filter(time_stamp__gte=start_time, time_stamp__lte=end_time).values()
#         day_used_kwh = [ i['meter_kwh'] for i in day_kwh ]
#         copykwh=day_used_kwh[::-1]
#         day_use_kwh=np.diff(copykwh)
#         day_used_power=sum(day_use_kwh)
#         context = {
#         'total_power':total_used_power,
#         'day_used_power':day_used_power,
#         }
#         return Response(context)
    
#                       @@@@@@@@@@@@ Power Calculation @@@@@@@@@@@

class Savecount(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        ############################# Day-wise kWh Calculation              
        current_day = date.today()

        month_start_time = datetime.combine(current_day.replace(day=1), datetime.min.time()) 
        print(month_start_time)
        next_month_start = current_day.replace(day=28) + timedelta(days=4)
        month_end_time = datetime.combine(next_month_start - timedelta(days=next_month_start.day), datetime.max.time())
        print(month_end_time)

        kwh_used_in_day = payload_power_mst.objects.filter(date=current_day).values('power_consume')
        sum_power_consume = kwh_used_in_day.aggregate(total_power_consume=Sum('power_consume'))
        power_consume_daily = sum_power_consume['total_power_consume']
        if power_consume_daily is not None:
            power_consume_daily=round(power_consume_daily,2)
        else:
            power_consume_daily=0


        power_save_in_day = payload_power_mst.objects.filter(date=current_day).values('power_save')
        sum_power_save = power_save_in_day.aggregate(total_power_save=Sum('power_save'))
        power_save_daily = sum_power_save['total_power_save']
        if power_save_daily is not None:
            power_save_daily=round(power_save_daily,2)
        else:
            power_save_daily=0

        
         
        ############################# Month-wise kWh Calculation

        kwh_used_monthly = payload_power_mst.objects.filter(date__range=[month_start_time,month_end_time]).aggregate(total_power_consume=Sum('power_consume'))
      
        power_consume_month = kwh_used_monthly['total_power_consume'] or 0
        power_consume_month=round(power_consume_month,2)


        powe_save_month = payload_power_mst.objects.filter(date__range=[month_start_time,month_end_time]).aggregate(total_power_save=Sum('power_save'))
        
        power_save_monthly = powe_save_month['total_power_save'] or 0
        power_save_monthly=round(power_save_monthly,2)



        ############################# Weekly wise kWh Calculation

        previous_week_start = current_day - timedelta(days=7)
        
        previous_week_start_time = datetime.combine(previous_week_start, datetime.min.time())
       
        current_date_end_time = datetime.combine(current_day, datetime.max.time())
       
       

        kwh_used_week = payload_power_mst.objects.filter(date__range=[previous_week_start_time,current_date_end_time]).values('date','power_consume','power_save')
        serializer=PayloadMstSerializer(kwh_used_week,many=True)
        weekly_list=serializer.data
        print('weekly_list',weekly_list)
        # date_power_dict = {item['date']: item['power_consume'] for item in kwh_used_week}
        weekly_power_consume_list = {item['date']: round(float(item['power_consume']),2) for item in weekly_list}

        weekly_power_save_list = {item['date']: round(float(item['power_save']),2) for item in weekly_list}
       
        
        
      
        sum_power_week = kwh_used_week.aggregate(total_power_consume=Sum('power_consume'))
        
        power_consume_week =  sum_power_week['total_power_consume']

        if power_consume_week is not None:
            power_consume_week=round(power_consume_week,2)
        else:
            power_consume_week =  sum_power_week['total_power_consume'] or 0




        powe_save_week = payload_power_mst.objects.filter(date__range=[previous_week_start_time,current_date_end_time]).values('power_save')
        sum_power_week = powe_save_week.aggregate(total_power_save=Sum('power_save'))
        power_save_week =  sum_power_week['total_power_save']

        if power_save_week is not None:
            power_save_week=round(power_save_week,2)
        else:
            power_save_week =  sum_power_week['total_power_save'] or 0



         


 
        context = {
        'power_consume_daily':power_consume_daily,
        'power_save_daily':power_save_daily,
        'power_consume_month':power_consume_month,
        'power_save_monthly':power_save_monthly,
        'power_consume_week':power_consume_week,
        'power_save_week':power_save_week,
        'weekly_power_consume_list':weekly_power_consume_list,
         'weekly_power_save_list':weekly_power_save_list,
        }
        return Response(context)


        
device_status = {"response": None}
print(device_status)

# Function to clear the response value after 10 seconds
def clear_response():
    global device_status
    print('yessss')
    time.sleep(2)
    device_status["response"] = None

@csrf_exempt
def device_uplink(request):
    print("*callllllllllllllllled Normal device_uplink ***")
    UplinkhandlerAPI(request).start()
    return HttpResponse("Okk ")

class UplinkhandlerAPI(threading.Thread):
    def __init__(self, request):
        self.request = request
        threading.Thread.__init__(self)

    def run(self):
        print('Run Start')
        data = self.request.body
        obj = json.loads(data)
        keysList = list(obj.keys())
        print('keysList' ,keysList)

        if "data" in keysList:
            print('Yes data in keysList')
            payload = base64.b64decode(obj['data']).hex()
            device_status['response']=payload
            print(device_status,'device_statusdevice_status')
            print('Received Payload',payload)
            if payload:
                print('Yes Payload is Working')
                try:
                    devEUI = base64.b64decode(obj['devEUI']).hex()
                    print(devEUI)
                    gw = base64.b64decode(obj['rxInfo'][0]['gatewayID']).hex()
                    print(gw)
                except:
                    devEUI = obj['devEUI']
                    gw = obj['rxInfo'][0]['gatewayID']
                print('***********************************gw',gw,devEUI)
                fq = obj['txInfo']['frequency']
                try:
                    sf = obj['txInfo']['loRaModulationInfo']['spreadingFactor']
                    print(sf,"SFFFFFFFFFFFFFFFFFFFFFFFF")
                except:
                    sf = '10'
                fcnt = obj['fCnt']
                modu = obj['applicationName']
                rssi = obj['rxInfo'][0]['rssi']
                snr = obj['rxInfo'][0]['loRaSNR']
                dataRate=obj['dr'] 
                # current_stamp=datetime.today()
                # print(current_stamp)
                # time_stamp= current_stamp
                # current_stamp.strftime("%Y-%m-%d-%H:%M:%S")
                payload = base64.b64decode(obj['data']).hex()
                
                post = uplinkdata() #data table
                post.deveui = devEUI
                post.payload = payload
                post.time_stamp=datetime.now()
                post.gateway_mac = gw
                post.frequency = fq
                post.applicationName = modu
                post.dataRate=dataRate
                post.rssi = rssi
                post.snr = snr
                post.fCnt = fcnt
                post.spreadingFactor = sf
                post.save()
                print('Data saved successfully in Uplinkdata Table')

                test_l=payload[0:4]

                print(test_l,"Test for L")
                byte_value = bytes.fromhex(test_l)
                ascii_value = byte_value.decode('ascii')
                print(ascii_value)
                l_list=['L0','L1','L2','L3','L4','L5','L6','L7','L8','L9']
                if ascii_value in l_list:
                    print('Yes L in List')
                    print("Calling payload_manager V4")
                    zone_thread = threading.Thread(target=payload_managerv4, args=(devEUI,payload))
                    zone_thread.start()
                else:
                    print("Calling Normal payload_manager ")
                    zone_thread = threading.Thread(target=payload_manager, args=(devEUI,payload))
                    zone_thread.start()

                # print("Calling payload_managerrrrrrrrrrrrrrrrrrrrrrrrrrr")
                # zone_thread = threading.Thread(target=payload_manager, args=(devEUI,payload))
                # zone_thread.start()
                # # downlink(devEUI,command)
            return HttpResponse("payload successfully recived  ")
        else:
            print('Data key is not in KeyList')
            return HttpResponse("payload not in correct format")
                
@csrf_exempt
def payload_manager(devEUI,payload):
# def payload_manager(request):
    print("####################***** Tesing *****#################")
     
    # payload='d8105f2d341a183006003219505020306300003c0200280f0f000053400943000000002654120175476142'
    # devEUI='50f0000000000ad2' 
    print('Yes Payload got successfully in Normal payload_manager',payload)
    status=payload[:2]

    print ("Initial string", status)
    reversed_status_bin=bin(int(status, 16))[2:].zfill(8)
    print(reversed_status_bin,"hex to bin")
    # reversed_status_bin=status_bin[::-1]
    # print(reversed_status_bin)

    if len(reversed_status_bin)==8:
        if reversed_status_bin[0]=='1':
            luc_detail='WithMeter'
            print(luc_detail,"LCU With Energy Meter")
        else:
            luc_detail='WithOutMeter'
            print(luc_detail,"(LCU Without Energy Meter")
            
        if reversed_status_bin[1]=='1':
            schedule_mode="Schedule Time" 
            print(schedule_mode,"schedule Mode – Schedule Time")
        else:
            schedule_mode="Real Time" 
            print(schedule_mode,"schedule Mode – Real Time")
        
        if reversed_status_bin[2]=='1':
            relay_status= 'ON'
            print(relay_status,"Relay Status – On")
        else:
            relay_status= 'OFF'
            print(relay_status,"Relay Status – OFF")
        
        if reversed_status_bin[3]=='1':
            power_grid_fail='Yes'
            print(power_grid_fail,"Power Fail - Yes")
        else:
            power_grid_fail='NO'
            print(power_grid_fail,"Power Fail – No")
            
        if reversed_status_bin[4]=='1':
                lamp_fali='Yes'
                print(lamp_fali,"Lamp Fail - Yes")
        else:
            lamp_fali='NO'
            print(lamp_fali,"Lamp Fail - NO")
            
        if reversed_status_bin[5]=='1':
            command_action_status="Yes"
            print(command_action_status,"Command Action - Yes")
        else:
            command_action_status="NO"
            print(command_action_status,"Command Action - No")
        
            
    timestamp=str(payload[2:12])
    print(timestamp,"timestamp")
    # time_stamp_pay=''
    # for i in range(0,len(str(timestamp)),2):
    #     p=i+2
    #     z=timestamp[i:p]
    #     d = int(z, base=16)
    #     print(d)
    #     if len(str(d))!=2:
    #         str(d).zfill(2)

    #     time_stamp_pay=f'{time_stamp_pay}{ str(d)}'
    # print(time_stamp_pay)
       
    # date_time = datetime.fromtimestamp( int(time_stamp_pay) )# final output
    # print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH") 
    # print(date_time)

    time_stamp_pay = ''
    for i in range(0, len(timestamp), 2):
        p = i + 2
        z = timestamp[i:p]
        d = int(z, base=16)
        print(d)
        
        # Check if the length is not 2, then add a leading '0'
        if len(str(d)) != 2:
            d = str(d).zfill(2)
            print(d)

        time_stamp_pay = f'{time_stamp_pay}{d}'

    print(time_stamp_pay)

    date_time = datetime.fromtimestamp(int(time_stamp_pay))  # final output
    print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    print(date_time ,"UTC Epoch Time ")
    
    sch_start_time=payload[12:16]
    print(sch_start_time,"sch_start_time")
    sch_start_time_db=sch_start_time[:2] +':' +sch_start_time[2:5] +':' +'00'
    print(sch_start_time_db,"Schedule Start Time")
    
    sch_end_time=payload[16:20]
    sch_end_time_db=sch_end_time[:2] +':' +sch_end_time[2:5] +':' +'00'
    print(sch_end_time_db,"Schedule End Time")
    
    default_dimming=payload[20:22]
    print(default_dimming,'default_dimming')
    if default_dimming != 0:
        default_dimming='5a'
    print(default_dimming,'default_dimming')
    default_dimming_per= int(default_dimming, 16)
    print( str(default_dimming_per),"Default Dimming")
    
    first_slot_time=payload[22:26]
    first_slot_time_db=first_slot_time[:2] +':' +first_slot_time[2:5] +':' +'00'
    print(first_slot_time_db,"Frist Slot Time(Dimming) ")
    
    first_slot_dimming=payload[26:28]
    print(first_slot_dimming)
    first_slot_dimming_per= int(first_slot_dimming, 16)
    print( str(first_slot_dimming_per),"Frist Slot Dimming ")
    
    second_slot_time=payload[28:32]
    second_slot_time_db=second_slot_time[:2] +':' +second_slot_time[2:5] +':' +'00'
    print(second_slot_time_db," Second Slot Time (Dimming)")
    
    second_slot_dimming=payload[32:34]
    second_slot_dimming_per= int(second_slot_dimming, 16)
    print( str(second_slot_dimming_per)," Second Slot (Dimming)")
    
    third_slot_time=payload[34:38]
    third_slot_time_db=third_slot_time[:2] +':' +third_slot_time[2:5] +':' +'00'
    print(third_slot_time_db," third Slot Time (Dimming)")
    
    third_slot_dimming=payload[38:40]
    third_slot_dimming_per= int(third_slot_dimming, 16)
    print( str(third_slot_dimming_per)," third Slot  (Dimming)")
    
    fourth_slot_time=payload[40:44]
    fourth_slot_time_db=fourth_slot_time[:2] +':' +fourth_slot_time[2:5] +':' +'00'
    print(fourth_slot_time_db," fourth Slot Time (Dimming)")
    
    fourth_slot_dimming=payload[44:46]
    print(fourth_slot_dimming,"fourth_slot_dimming")
    fourth_slot_dimming_per= int(fourth_slot_dimming, 16)
    print( str(fourth_slot_dimming_per)," fourth Slot (Dimming)")
    
    meter_interval=payload[46:48]
    print(meter_interval,"meter_intervals")
    meter_interval_db= int(meter_interval, 16)
    print( str(meter_interval_db),"Meter Data Interval ")
    
    
    current_dimming=payload[48:50]

    print(current_dimming,"DEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
    current_dimming_db= int(current_dimming, 16)
    print( str(current_dimming_db),"Current Dimming ")
    
    
    meter_kwh=payload[50:58]
    print(meter_kwh)
    meter_kwh_db= (int(meter_kwh, 16))/1000
    print( str(meter_kwh_db),"Meter Data (kWh) ")
    
    meter_voltage=payload[58:62]
    meter_voltag_db= (int(meter_voltage, 16))/10
    print( str(meter_voltag_db),"Meter Data (Voltage)")
    
    meter_current=payload[62:70]
    meter_current_db= (int(meter_current, 16))/1000
    print( str(meter_current_db),"Meter Data (Current)")
    
    gps_lat=payload[70:78]
    lat_db=gps_lat[0:2] +'.' + gps_lat[2:]
    print(gps_lat)
    print(lat_db,"GPS Lat ")
    
    gps_long=payload[78:86]
    long_db=gps_long[0:2] +'.' + gps_long[2:]
    print(gps_long)
    print(long_db,"GPS Long")

    gps_lat_long= str(lat_db + "," + long_db)
    print(gps_lat_long,"GPS lat/Long")
    
    reversed_byte=payload[86:]
    print(reversed_byte)
    print(date_time)
    print(status)
    print(timestamp)
    print(sch_start_time)
    print(sch_end_time)
    print(default_dimming)
    print(first_slot_time)
    print(first_slot_dimming)
    print(second_slot_time)
    print(second_slot_dimming)
    print(third_slot_time)
    print(third_slot_dimming)
    print(fourth_slot_time)
    print(fourth_slot_dimming)
    print(meter_interval)
    print(current_dimming)
    print(meter_kwh)
    print(meter_voltage)
    print(meter_current)
    print(gps_lat_long)
    print(reversed_byte)
  
    
    print('Add payload data in db')
    matching_dev = device_register_details.objects.get(dev_eui=devEUI)
    ward_nam=matching_dev.device_ward
    zone_nam=matching_dev.device_zone
    print(matching_dev)

    print(ward_nam)
    post=payloaddata()
    post.device=matching_dev
    post.devEUI = devEUI
    post.status=reversed_status_bin
    post.luc_detail=luc_detail
    post.schedule_mode=schedule_mode
    post.relay_status=relay_status
    post.power_grid_fail=power_grid_fail
    post.lamp_fali=lamp_fali 
    post.command_action_status=command_action_status
    post.time_stamp= date_time
    post.sch_start_time=sch_start_time_db
    post.sch_end_time=sch_end_time_db
    post.default_dimming=default_dimming_per
    post.first_slot_time=first_slot_time_db 
    post.first_slot_dimming=first_slot_dimming_per
    post.second_slot_time=second_slot_time_db 
    post.second_slot_dimming=second_slot_dimming_per
    post.third_slot_time= third_slot_time_db
    post.third_slot_dimming= third_slot_dimming_per
    post.fourth_slot_time= fourth_slot_time_db
    post.fourth_slot_dimming=fourth_slot_dimming_per
    post.meter_data_interval= meter_interval_db
    post.current_dimming= current_dimming_db
    post.meter_kwh=meter_kwh_db
    post.meter_voltage =meter_voltag_db
    post.meter_current=meter_current
    post.latitude=lat_db
    post.longitude=long_db
    
    current_date = date.today()

    # power used for single device in one day 
    day_start_time = datetime.combine(current_date, datetime.min.time())
    day_end_time = datetime.combine(current_date, datetime.max.time())
    last_kwh_data = payloaddata.objects.filter(devEUI=str(devEUI), time_stamp__range=[day_start_time,day_end_time]).values().last()
    print(last_kwh_data,'last_kwh_datalast_kwh_datalast_kwh_data')
    last_kwh = 0
    if last_kwh_data is not None:
        last_kwh = last_kwh_data['meter_kwh']
        print(last_kwh,'last_kwhlast_kwhlast_kwhlast_kwh')
    else:
        last_kwh=0
    print(meter_kwh_db,'meter_kwh_dbmeter_kwh_dbmeter_kwh_db')
    new_meter_kwh=meter_kwh_db - last_kwh
    print(new_meter_kwh)
    post.save()
    print("Data successfully inserted in DB")

    print("Calling payloaddata_power for KWH check")
    mst_thread = threading.Thread(target=payloaddata_power, args=(devEUI,new_meter_kwh,relay_status,ward_nam,zone_nam))
    mst_thread.start() 
    

    return HttpResponse("Okk............................................. ")


# payload_manager('50f0000000000ad2','301107205126173717411417385a1739141739631740140f1400000000000000000000ffffffffffffffff')
@csrf_exempt
def payloaddata_power(devEUI,new_meter_kwh,relay_status,ward_nam,zone_nam):
    print("**** Yes Data received in payloaddata_power")
    
    print('Received data ',devEUI,new_meter_kwh,relay_status,ward_nam,zone_nam)

    current_date = date.today()
    day_start_time = datetime.combine(current_date, datetime.min.time()) 
    day_end_time = datetime.combine(current_date, datetime.max.time())
    
    # Extract the dimming values and timestamps
    new_consume_power = payloaddata.objects.filter(devEUI=devEUI, time_stamp__range=[day_start_time, day_end_time]).values().last()
    print(new_consume_power)
    if new_consume_power is not None:
        dimming_values = [
            new_consume_power['first_slot_dimming'],
            new_consume_power['second_slot_dimming'],
            new_consume_power['third_slot_dimming'],
            new_consume_power['fourth_slot_dimming']
        ]
        timestamps = [
            new_consume_power['first_slot_time'],
            new_consume_power['second_slot_time'],
            new_consume_power['third_slot_time'],
            new_consume_power['fourth_slot_time']
        ]
        print(dimming_values)
        print(timestamps)
        # Find the index of the maximum dimming value
        max_dimming_index = dimming_values.index(max(dimming_values))
        print(max_dimming_index)
        # Get the maximum dimming time and the next time slot

        max_dimming_time = datetime.combine(datetime.today().date(), timestamps[max_dimming_index])
        print(max_dimming_time)
        next_time_slot_index = (max_dimming_index + 1) % len(timestamps)
        print(next_time_slot_index)
        next_time_slot = datetime.combine(datetime.today().date(), timestamps[next_time_slot_index])
        print(next_time_slot)

        # Adjust time for 00:00:00 as 24:00:00

        if max_dimming_time.time() == datetime.min.time():
            max_dimming_time += timedelta(days=1)
        print(max_dimming_time,'MAAXXXXXXXXXXXXXXXXXXXXXX')    
        if next_time_slot.time() == datetime.min.time():
            next_time_slot += timedelta(days=1)
        print(next_time_slot,'SFFFFFFFFFFFFFFFFFFFFFFFF')

        # Calculate the time difference in hours

        time_diff = (next_time_slot - max_dimming_time).total_seconds() / 3600

        print(time_diff,'HHH')

        # Calculate the sum of 'meter_kwh' for the day starting from the maximum dimming time

        # day_hight_kwh = payloaddata.objects.filter(devEUI=dev_EUI, time_stamp__range=[max_dimming_time,next_time_slot]).values('meter_kwh').aggregate(total_kwh=Sum('meter_kwh'))['total_kwh']
        day_hight_kwh = payloaddata.objects.filter(devEUI=devEUI, time_stamp__range=[max_dimming_time,next_time_slot]).values('meter_kwh')
        print(day_hight_kwh,"HIkkkkkkkkkkkkkkk")
        kwh_list = [ i['meter_kwh'] for i in day_hight_kwh ]
         
        kwn_data=np.diff(kwh_list)
        total_day_hight_kwh=sum(kwn_data)

        print(total_day_hight_kwh,'hhhhhhhhhhhhhhhhhhhhhhhhhh')
        

        # Get the sch_start_time and sch_end_time columns

        sch_start_time = new_consume_power['sch_start_time']
        print(sch_start_time)
        sch_end_time = new_consume_power['sch_end_time']
        print(sch_end_time)
 
        if sch_start_time == datetime.min.time():
            sch_start_time = timedelta(days=1)
        if sch_end_time == datetime.min.time():
            sch_end_time = timedelta(days=1)

        # Calculate the time difference between sch_start_time and sch_end_time in hours
        sch_time_diff = abs((datetime.combine(datetime.today().date(), sch_end_time) - datetime.combine(datetime.today().date(), sch_start_time))).total_seconds() / 3600
        print(sch_time_diff)
        power_used__high_dim =(total_day_hight_kwh / time_diff) * sch_time_diff
        print(power_used__high_dim)
       
        print('power_used__high_dim',power_used__high_dim)

    total_power_save =(power_used__high_dim) - (new_meter_kwh)

    print(total_power_save,'ssssssssssssssssssssssssssssss')
    existing_record = payload_power_mst.objects.filter(device_eui=devEUI, date=current_date).last()
    try:
        fk_device = device_register_details.objects.get(dev_eui=devEUI)
    except device_register_details.DoesNotExist:
        return Response({"error": "Device not found"}, status=status.HTTP_400_BAD_REQUEST)
    print(zone_nam)
    if existing_record:
        existing_record.power_consume = new_meter_kwh
        existing_record.power_save = total_power_save
        existing_record.device_on_off=relay_status
        existing_record.save()  
    else:
        # Record doesn't exist, create a new row and update the data
        new_record = payload_power_mst(fk_device=fk_device,device_eui=devEUI, zone_name=zone_nam, ward_name=ward_nam, date=current_date, power_consume=new_meter_kwh, power_save=total_power_save,device_on_off=relay_status)
        new_record.save()
    return HttpResponse('ok')
   
# @csrf_exempt              
# def downlink( devEUI, command):
#     print('****************************************************************************************************')
#     lora_login_url = "http://3.111.136.195"
#     username = "admin"
#     password = "admin"
#     headers_login = {
#         "Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
#     ###las login and meter command####
#     url_login = lora_login_url+":8080/api/internal/login"
#     print('****************************************************')
#     try:
#         payload_login = {"password": password, "email": username}
#         print('**********************************345*', payload_login)
#         payload_login = json.dumps(payload_login)
#         print(payload_login, '6666666')
#         response = requests.post(
#             url_login, data=payload_login, headers=headers_login, verify=False)
#         print("response is as ***", response.text)
#     except:
#         payload_login = {"password": password, "username": username}
#         payload_login = json.dumps(payload_login)
#         print(payload_login)
#         response = requests.post(
#         url_login, data=payload_login, headers=headers_login, verify=False)
#     jwt = json.loads(response.text)
#     print(jwt)
#     token = jwt['jwt']
#     headers = {"Content-type": "application/x-www-form-urlencoded",
#             "Accept": "text/plain", "Grpc-Metadata-Authorization": token}
#     url = lora_login_url+":8080/api/devices/"+devEUI+"/queue"

    
#     b64 = codecs.encode(codecs.decode(command, 'hex'), 'base64').decode()
#     print("hex to base64  ", b64)
#     data = {
#         "deviceQueueItem": {
#             "confirmed": True,
#             "data": b64,
#             "devEUI": devEUI,
#             "fCnt": 0,
#             "fPort": 7
#         }
#     }
#     data = json.dumps(data)
#     print(data)
     
#     response = requests.post(url, data=data, headers=headers, verify=False)
#     print(response)
#     return HttpResponse("Okk Downlink send............................................. ")


    ################### Commands##################
# @api_view(['GET', 'POST'])
def downlink_commands(devEUI, command):
    print('****************************************************************************************************')

    lora_login_url = "http://testing.siotel.in"
    username = "root@admin"
    password = "Use@me"
    headers_login = {
        "Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    ###las login and meter command####
    url_login = lora_login_url+":8080/api/internal/login"
     
    try:
        payload_login = {"password": password, "email": username}
         
        payload_login = json.dumps(payload_login)
         
        response = requests.post(
            url_login, data=payload_login, headers=headers_login, verify=False)
        
    except:
        payload_login = {"password": password, "username": username}
        payload_login = json.dumps(payload_login)
         
        response = requests.post(
        url_login, data=payload_login, headers=headers_login, verify=False)
    jwt = json.loads(response.text)
    
    token = jwt['jwt']
    headers = {"Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain", "Grpc-Metadata-Authorization": token}
    url = lora_login_url+":8080/api/devices/"+devEUI+"/queue"

    
    b64 = codecs.encode(codecs.decode(command, 'hex'), 'base64').decode()
     
    data = {
        "deviceQueueItem": {
            "confirmed": True,
            "data": b64,
            "devEUI": devEUI,
            "fCnt": 0,
            "fPort": 7
        }
    }
    data = json.dumps(data)
   
     
    response = requests.post(url, data=data, headers=headers, verify=False)
    print(response,'responseeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    # status_code = response.status_code
    # print(status_code,'responseeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    return Response("OKK")
 
@csrf_exempt
@api_view(['GET', 'POST'])
def setstatus_command(request, devEUI, ctype, command):
    print(devEUI)
    print(ctype)
    print(command)

    if request.method == "GET":
        print('yes')
        if str(ctype) == 'time':
            print('time')
            hex_command=command.replace('-','').replace('T','').replace(':','')
            if len(hex_command)!=14:
                new_command=str(hex_command)+'00'
            print(new_command)

            my_fix_command='L0|'+new_command+'*'
            print(my_fix_command,'hex_commandhex_commandh')

            command = ''.join([hex(ord(char))[2:] for char in my_fix_command])
            print(command,'commandcommandcommandcommand')
            result = downlink_commands(devEUI, command)
            time.sleep(8)
            status_code = result.status_code
            status=device_status.get('response')
            if status_code == 200 and status is not None :
                byte_value = bytes.fromhex(status)
                # Convert the bytes to ASCII
                ascii_value = byte_value.decode('ascii')
                print(ascii_value,'statusstatusstatusstatusstatusstatusstatusstatusstatus')
                return Response(ascii_value)
            else:
                return HttpResponse('Failed')
             


        elif str(ctype) == 'dim':
            print('dim')
            my_fix_command='L2|'+str(command)+'*'
            print(my_fix_command,'hex_commandhex_commandh')
            new_dim=command
            command = ''.join([hex(ord(char))[2:] for char in my_fix_command])
            print(command,'commandcommandcommandcommand')
            result = downlink_commands(devEUI, command)
            time.sleep(8)
            status_code = result.status_code
            status=device_status.get('response')
            if status_code == 200 and status is not None :
                byte_value = bytes.fromhex(status)
                # Convert the bytes to ASCII
                ascii_value = byte_value.decode('ascii')
                print(ascii_value,'statusstatusstatusstatusstatusstatusstatusstatusstatus')
                latest_record = payloaddata.objects.filter(devEUI=devEUI).latest('time_stamp')
                new_values = {
                    'current_dimming': new_dim,   
                }
         
                # Update the latest record with the new values
                for field, value in new_values.items():
                    setattr(latest_record, field, value)
                print('data save')
                latest_record.save()
                return Response(ascii_value)
            else:
                return HttpResponse('Failed')

             

        elif str(ctype) == 'mode':
            if str(command)=='real':
                my_fix_command='L4|R*'
                print(my_fix_command)
                command = ''.join([hex(ord(char))[2:] for char in my_fix_command])
                result = downlink_commands(devEUI, command)
                time.sleep(8)
                status_code = result.status_code
                status=device_status.get('response')
                if status_code == 200 and status is not None :
                    byte_value = bytes.fromhex(status)
                    # Convert the bytes to ASCII
                    ascii_value = byte_value.decode('ascii')
                    print(ascii_value,'statusstatusstatusstatusstatusstatusstatusstatusstatus')
                    latest_record = payloaddata.objects.filter(devEUI=devEUI).latest('time_stamp')
                    new_values = {
                        'schedule_mode': 'Real',   
                    }
             
                    # Update the latest record with the new values
                    for field, value in new_values.items():
                        setattr(latest_record, field, value)
                    latest_record.save()

                    return Response(ascii_value)
                else:
                    return HttpResponse('Failed')
                
            else:
                my_fix_command='L4|S*'
                print(my_fix_command)
                command = ''.join([hex(ord(char))[2:] for char in my_fix_command])
                result = downlink_commands(devEUI, command)
                time.sleep(8)
                status_code = result.status_code
                status=device_status.get('response')
                if status_code == 200 and status is not None :
                    byte_value = bytes.fromhex(status)
                    # Convert the bytes to ASCII
                    ascii_value = byte_value.decode('ascii')
                    print(ascii_value,'statusstatusstatusstatusstatusstatusstatusstatusstatus')
                    latest_record = payloaddata.objects.filter(devEUI=devEUI).latest('time_stamp')
                    new_values = {
                        'schedule_mode': 'Schedule',   
                    }
             
                    # Update the latest record with the new values
                    for field, value in new_values.items():
                        setattr(latest_record, field, value)
                    latest_record.save()

                    return Response(ascii_value)
                else:
                    return HttpResponse('Failed')
                


        elif str(ctype) == 'interval':
            print('interval')
            new_int=command
            if len(command)!=3:
                new_command='0'+str(command)
                my_fix_command='L8|'+new_command+'*'
                print(my_fix_command)
                command = ''.join([hex(ord(char))[2:] for char in my_fix_command])
                result = downlink_commands(devEUI, command)
                time.sleep(8)
                status_code = result.status_code
                status=device_status.get('response')
                if status_code == 200 and status is not None :
                    byte_value = bytes.fromhex(status)
                    # Convert the bytes to ASCII
                    ascii_value = byte_value.decode('ascii')
                    print(ascii_value,'statusstatusstatusstatusstatusstatusstatusstatusstatus')
                    latest_record = payloaddata.objects.filter(devEUI=devEUI).latest('time_stamp')
                    new_values = {
                        'meter_data_interval': new_int,   
                    }
             
                    # Update the latest record with the new values
                    for field, value in new_values.items():
                        setattr(latest_record, field, value)
                    latest_record.save()
                    print('data save successfully')

                    return Response(ascii_value)
                else:
                    return HttpResponse('Failed')
                 
            else:
                my_fix_command='L4|'+str(command)+'*'
                print(my_fix_command)
                command = ''.join([hex(ord(char))[2:] for char in my_fix_command])
                result = downlink_commands(devEUI, command)
                time.sleep(8)
                status_code = result.status_code
                status=device_status.get('response')
                if status_code == 200 and status is not None :
                    byte_value = bytes.fromhex(status)
                    # Convert the bytes to ASCII
                    ascii_value = byte_value.decode('ascii')
                    print(ascii_value,'statusstatusstatusstatusstatusstatusstatusstatusstatus')
                    latest_record = payloaddata.objects.filter(devEUI=devEUI).latest('time_stamp')
                    new_values = {
                        'meter_data_interval': new_int,   
                    }
             
                    # Update the latest record with the new values
                    for field, value in new_values.items():
                        setattr(latest_record, field, value)
                    latest_record.save()
                    return Response(ascii_value)
                else:
                    return HttpResponse('Failed')
                 
                 
        elif str(ctype)=='rtc':
            hex_command=command.replace('-','').replace('T','').replace(':','')
            if len(hex_command)!=14:
                new_command=str(hex_command)+'00'
            print(new_command)
            date_c=new_command[:8]
            time_c=new_command[8:]
            c_date=str(date_c[6:])+str(date_c[4:6])+'04'+str(date_c[2:4])
            my_fix_command='L9|'+str(time_c)+'|'+str(c_date)+'*'
            print(my_fix_command)
            command = ''.join([hex(ord(char))[2:] for char in my_fix_command])
            result = downlink_commands(devEUI, command)
            time.sleep(8)
            status_code = result.status_code
            status=device_status.get('response')
            if status_code == 200 and status is not None :
                byte_value = bytes.fromhex(status)
                # Convert the bytes to ASCII
                ascii_value = byte_value.decode('ascii')
                print(ascii_value,'statusstatusstatusstatusstatusstatusstatusstatusstatus')
                return Response(ascii_value)
            else:
                return HttpResponse('Failed')
            
        else:
         
            return Response('HTTP_400_BAD_REQUEST.............')       
    else:
        return HttpResponse("HTTP_400_BAD_REQUEST.............")
 
@csrf_exempt
@api_view(["POST"])
def set_schedule_command(request):
    obj=request.data
    print(obj)
    devEUI=obj['dev_eui']
    start_time=obj['stime'].replace(':','')
    end_time=obj['etime'].replace(':','')
    default_dimming=obj['ddim']
    relay_status=obj['rstatus']
    f_sch_time=obj['fstime'].replace(':','')
    f_sch_dim_p=obj['fshdp']
    s_sch_time=obj['sstime'].replace(':','')
    s_sch_dim_p=obj['sshdp']
    t_sch_time=obj['tstime'].replace(':','')
    t_sch_dim_p=obj['tshdp']
    fo_sch_time=obj['fostime'].replace(':','')
    fo_sch_dim_p=obj['foshdp']


    print(devEUI)
    print(start_time)
    print(end_time)
    print(default_dimming)
    print(relay_status)
    print(f_sch_time)
    print(f_sch_dim_p)
    print(s_sch_dim_p)
    print(s_sch_dim_p)
    print(t_sch_time)
    print(t_sch_dim_p)
    print(fo_sch_time)
    print(fo_sch_dim_p)

    my_fix_command='L1|'+str(start_time)+'|'+str(end_time)+'|'+str(relay_status)+'|'+str(default_dimming)+'|'+str(f_sch_time)+'|'+str(f_sch_dim_p)+'|'+str(s_sch_time)+'|'+str(s_sch_dim_p)+'|'+str(t_sch_time)+'|'+str(t_sch_dim_p)+'|'+str(fo_sch_time)+'|'+str(fo_sch_dim_p)+'*'
     
    print(my_fix_command)
    command = ''.join([hex(ord(char))[2:] for char in my_fix_command])
    print(command)
    result = downlink_commands(devEUI, command)
    status_code = result.status_code
    time.sleep(8)
    status_code = result.status_code
    status=device_status.get('response')
    if status_code == 200 and status is not None :
        # Get the latest record based on the timestamp field (e.g., date_time)
        latest_record = payloaddata.objects.filter(devEUI=devEUI).latest('time_stamp')
        new_values = {
            'sch_start_time': obj['stime'],
            'sch_end_time': obj['etime'],
            'default_dimming': default_dimming,
            'first_slot_time': obj['fstime'],
            'first_slot_dimming': f_sch_dim_p,
            'second_slot_time': obj['sstime'],
            'second_slot_dimming': s_sch_dim_p,
            'third_slot_time': obj['tstime'],
            'third_slot_dimming': t_sch_dim_p,
            'fourth_slot_time': obj['fostime'],
            'fourth_slot_dimming': fo_sch_dim_p,
            'relay_status': relay_status,
        }
 
        # Update the latest record with the new values
        for field, value in new_values.items():
            setattr(latest_record, field, value)
        latest_record.save()

        print('Latest Record Updated')
  
        byte_value = bytes.fromhex(status)
        # Convert the bytes to ASCII
        ascii_value = byte_value.decode('ascii')
        print(ascii_value,'statusstatusstatusstatusstatusstatusstatusstatusstatus')
        return Response(ascii_value)
     
    # if status_code == 200:
    #     time.sleep(5)
    #     status = device_status.get('response')
    #     if status is not None:  # Corrected the 'if' statement here
    #         byte_value = bytes.fromhex(status)
    #         ascii_value = byte_value.decode('ascii')
    #         print(ascii_value, 'statusstatusstatusstatusstatusstatusstatusstatusstatus')
    #         return Response(ascii_value)
    #     else:
    #         return Response('HTTP_400_BAD_REQUEST.............')
    else:
        return Response('HTTP_400_BAD_REQUEST.............')



   # Import your model here if not already done
@csrf_exempt
def device_uplinkv4(request):
    print("*callllllllllllllllledV4***")
    UplinkhandlerAPIV4(request).start()
    return HttpResponse("Okk ")

class UplinkhandlerAPIV4(threading.Thread):
    def __init__(self, request):
        self.request = request
        threading.Thread.__init__(self)

    def run(self):
        data = self.request.body
        print(data, 'hhhhh')
        obj = json.loads(data)
        keysList = list(obj.keys())
        print(keysList, 'dddddddddddddddddddddddddddddddddddddd')

        if "data" in keysList:
            payload = base64.b64decode(obj['data']).hex()
            device_status['response'] = payload
            print(payload, "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            if payload:
                try:
                    devEUI = obj['deviceInfo']['devEui']
                    gw = obj['rxInfo'][0]['gatewayId']  # Changed 'gatewayID' to 'gatewayId'
                    print(devEUI)
                    print(gw)
                except:
                    devEUI = base64.b64decode(obj['devEUI']).hex()
                    gw = base64.b64decode(obj['rxInfo'][0]['gatewayId']).hex()  # Changed 'gatewayID' to 'gatewayId'

                print('***********************************gw', gw, devEUI)
                fq = obj['txInfo']['frequency']
                try:
                    sf = obj['txInfo']['modulation']['lora']['spreadingFactor']  # Corrected the key path
                    print(sf, "SFFFFFFFFFFFFFFFFFFFFFFFF")
                except:
                    sf = '10'
                fcnt = obj['fCnt']
                modu = obj['deviceInfo']['applicationName']  # Corrected the key path
                rssi = obj['rxInfo'][0]['rssi']
                snr = obj['rxInfo'][0]['snr']  # Corrected 'loRaSNR' to 'snr'
                dataRate = obj['dr']
                current_stamp = datetime.today()
                time_stamp = current_stamp.strftime("%Y-%m-%d-%H:%M:%S")
                payload = base64.b64decode(obj['data']).hex()

                post = uplinkdata()  # data table
                post.deveui = devEUI
                post.payload = payload
                post.time_stamp = time_stamp
                post.gateway_mac = gw
                post.frequency = fq
                post.applicationName = modu
                post.dataRate = dataRate
                post.rssi = rssi
                post.snr = snr
                post.fCnt = fcnt
                post.spreadingFactor = sf
                post.save()
                test_l=payload[0:4]
                byte_value = bytes.fromhex(test_l)
                ascii_value = byte_value.decode('ascii')
                print(ascii_value)
                l_list=['L0','L1','L2','L3','L4','L5','L6','L7','L8','L9']
                if ascii_value in l_list:
                    print("Calling payload_managerrrrrrrrrrrrrrrrrrrrrrrrrrrV44444")
                    zone_thread = threading.Thread(target=payload_managerv4, args=(devEUI,payload))
                    zone_thread.start()
                    # downlink(devEUI,command)
                else:
                    print("Calling payload_managerrrrrrrrrrrrrrrrrrrrrrrrrrr")
                    zone_thread = threading.Thread(target=payload_manager, args=(devEUI,payload))
                    zone_thread.start()

            return HttpResponse("Payload successfully received  ")
        else:
            return HttpResponse("Payload not in correct format")



                
@csrf_exempt
def payload_managerv4(devEUI,payload):
    print('Data received in payload_managerv4 for L Type')
# def payload_managerv4(request):
    # payload='4c367c307c32303032307c353030377c323435377c3333377c39357c37397c38327c32342a'
    print('Received payload',payload)
    
    byte_value = bytes.fromhex(payload)
    new_pay = byte_value.decode('ascii')
    print(new_pay,'new')
    new_pay=new_pay.split('|')
    print('After Split payload ',new_pay)

    ascii_value = new_pay[0]
    print(ascii_value)

    if ascii_value=='L4':
        print('yes working for L4')
        mode=new_pay[1].replace('*','')
        if mode==0:
            latest_record = payloaddata.objects.filter(devEUI=devEUI, time_stamp__date=current_date).latest('time_stamp')
            latest_record.schedule_mode = 'Real'
            latest_record.save()
            print('Mode updated successfully in payloaddata table for L4')
            return HttpResponse("payload successfully recived  ")




    if ascii_value=='L5':
        print('yes working for L5')
        on_off=new_pay[1]
        # byte_value = bytes.fromhex(on_off)
        # on_offs = byte_value.decode('ascii')
        if on_off==1:
            on_off_status='ON'
        else:
            on_off_status='OFF'
        mode=new_pay[2]
        # byte_value = bytes.fromhex(mode)
        # modes = byte_value.decode('ascii')

        if str(mode)=='R':
            set_mode='Real'
            current_date=new_pay[3]
            current_time=new_pay[4]
            current_timess=current_date+' '+current_time
            print(current_timess)
 
            relay_on_off=new_pay[5]
            if relay_on_off=='1':
                relay_on_off='ON'
            else:
                relay_on_off='OFF'
            print(relay_on_off)
             
            dimming_value=new_pay[6]
            print(dimming_value)
            meter_interval=new_pay[7].replace('*','')
            print(meter_interval)

            current_date = date.today()

            try:
                # Try to find the latest record for the specified devEUI and current date
                latest_record = payloaddata.objects.filter(devEUI=devEUI, time_stamp__date=current_date).latest('time_stamp')

                # If a record exists, update the latest row
                latest_record.time_stamp = datetime.now()
                latest_record.default_dimming = dimming_value
                latest_record.meter_data_interval = meter_interval
                latest_record.schedule_mode=set_mode
                latest_record.relay_status=relay_on_off
                latest_record.save()
                print('Data updated successfully in payloaddata table for L5')

            except payloaddata.DoesNotExist:
                # If no record exists for the specified devEUI and current date, create a new one
                matching_dev = device_register_details.objects.get(dev_eui=devEUI)
                post = payloaddata(
                    device=matching_dev,
                    devEUI=devEUI,
                    time_stamp=datetime.now(),
                    # date=current_date,  # Include the current date
                    default_dimming=dimming_value,
                    meter_data_interval=meter_interval,
                    schedule_mode=set_mode,
                    relay_status=relay_on_off,
                )
                post.save()
                print('Data saved successfully in payloaddata table for L5')
             
             
        elif str(mode)=='S':
            set_mode='Schedule'
            current_date=new_pay[3]
            current_time=new_pay[4]
            current_timess=current_date+' '+current_time
            print(current_timess)

            start_time=new_pay[5]
            time_obj=datetime.strptime(start_time, "%H%M")
            start_timess=time_obj.strftime("%H:%M:%S")

            end_time=new_pay[6]
            time_obj=datetime.strptime(end_time, "%H%M")
            end_timess=time_obj.strftime("%H:%M:%S")

            relay_on_off=new_pay[7]
            if relay_on_off=='1':
                relay_on_off='ON'
            else:
                relay_on_off='OFF'

            print(relay_on_off)
            dimming_value=new_pay[8]
            print(dimming_value)

            meter_interval=new_pay[9].replace('*','')
            print(meter_interval)


            current_date = date.today()

            try:
                # Try to find the latest record for the specified devEUI and current date in payloaddata
                latest_record = payloaddata.objects.filter(devEUI=devEUI, time_stamp__date=current_date).latest('time_stamp')

                # If a record exists, update the latest row in payloaddata
                latest_record.time_stamp = current_timess
                latest_record.sch_start_time = start_timess
                latest_record.sch_end_time = end_timess
                latest_record.default_dimming = dimming_value
                latest_record.meter_data_interval = meter_interval
                latest_record.schedule_mode=set_mode
                latest_record.relay_status=relay_on_off
                latest_record.save()
                print('Data saved successfully in payloaddata table for L5')

            except payloaddata.DoesNotExist:
                # If no record exists for the specified devEUI and current date in payloaddata, create a new one
                matching_dev = device_register_details.objects.get(dev_eui=devEUI)
                post = payloaddata(
                    device=matching_dev,
                    devEUI=devEUI,
                    time_stamp=current_timess,
                    # date=current_date,  # Include the current date
                    sch_start_time=start_timess,
                    sch_end_time=end_timess,
                    default_dimming=dimming_value,
                    meter_data_interval=meter_interval,
                    schedule_mode=set_mode,
                    relay_status=relay_on_off,
                )
                post.save()
                print('Data saved successfully in payloaddata table for L5') 
        return HttpResponse("payload successfully recived  ")
        
    elif ascii_value=='L6':
        print('yes working for L6')
        on_offs=new_pay[1]
        
        if on_offs==1:
            on_off_status='ON'
        else:
            on_off_status='OFF'
        print(on_off_status)
        total_kwh=new_pay[2]
        print(total_kwh)
    
        total_kwhss=int(total_kwh)/1000
        print(total_kwhss)
        
        freq=new_pay[3]
        print(freq)
        # freqs = freq.encode('utf-8').hex()
        freqss=int(freq)/100 
        print(freqss)

        vtg=new_pay[4]
        print(vtg)
        # vtgs = vtg.encode('utf-8').hex()
        
        vtgss=int(vtg)/10
        print(vtgss)

        current=new_pay[5]
        print(current)
        # currents = current.encode('utf-8').hex()
        currentss=int(current)/1000

        print(currentss)

        pf=new_pay[6]
        print(pf)

        # pfs = pf.encode('utf-8').hex()
        pfss=int(pf)/100
        print(pfss)

        actv_pwr=new_pay[7]
        print(actv_pwr)
        # actv_pwrs = actv_pwr.encode('utf-8').hex()
        actv_pwrss=int(actv_pwr)/1000
        print(actv_pwrss)

        apprnt_pwr=new_pay[8]
        print(apprnt_pwr,'apprnt_pwr')
        # apprnt_pwrs = apprnt_pwr.encode('utf-8').hex()
        apprnt_pwrss=int(apprnt_pwr)/1000
        print(apprnt_pwrss)

        ractv_pwr=new_pay[9]
        ractv_pwr=ractv_pwr.replace('*','')
        print(ractv_pwr)
        # ractv_pwrs = ractv_pwr.encode('utf-8').hex()
        ractv_pwrss=int(ractv_pwr)/1000

        current_date = date.today()
        matching_dev = device_register_details.objects.get(dev_eui=devEUI)
        zone_name = matching_dev.device_zone
        ward_name = matching_dev.device_ward
        latitude=matching_dev.device_latitude
        longitude=matching_dev.device_longitude
        device_type=matching_dev.device_type

        # Find the latest record for the current date with the matching devEUI in payloaddata
        try:
            latest_record = payloaddata.objects.filter(devEUI=devEUI, time_stamp__date=current_date).latest('time_stamp')

            # If a record exists, update the latest row
            new_values = {
                'time_stamp': datetime.now(),
                'meter_voltage': vtgss,
                'meter_current': currentss,
                'relay_status': on_off_status,
                'meter_kwh': total_kwhss,
                'latitude':latitude,
                'longitude':longitude,
                'luc_detail':device_type,
            }

            # Update the latest record with the new values
            for field, value in new_values.items():
                setattr(latest_record, field, value)
            latest_record.save()
            print('Data updated successfully in payloaddata')

        except payloaddata.DoesNotExist:
            # If no record exists, create a new one in payloaddata
            matching_dev = device_register_details.objects.get(dev_eui=devEUI)

            create_new = payloaddata.objects.create(
                device=matching_dev,
                devEUI=devEUI,
                meter_kwh=total_kwhss,
                meter_voltage=vtgss,
                meter_current=currentss,
                time_stamp=datetime.now(),
                relay_status=on_off_status,
                latitude=latitude,
                longitude=longitude,
                luc_detail=device_type,
            )
            print('New record created and data saved successfully in payloaddata')

        
        # Find the latest record for the current date
        last_power_consume = payload_power_mst.objects.filter(device_eui=devEUI, date=current_date).last()
        if last_power_consume is None:
            exists_powers=0

            new_record = payload_power_mst(
            fk_device=matching_dev,
            device_eui=devEUI,
            power_consume=total_kwhss,
            date=current_date,
            device_on_off=on_off_status,
            zone_name=zone_name,
            ward_name=ward_name,
            )
            new_record.save()
            print('New record created and data saved successfully for Power')
        else:
            # Calculate new power consumption
            exists_powers = last_power_consume.power_consume
            new_power_consume = float(total_kwhss) - float(exists_powers)
            new_total_power_consume=float(new_power_consume) + float(exists_powers)

            # Update the latest record with the new values
            last_power_consume.zone_name = zone_name
            last_power_consume.ward_name = ward_name
            last_power_consume.device_on_off = on_off_status
            last_power_consume.power_consume = new_total_power_consume
            last_power_consume.save()
            print('Data updated successfully for Power')

        return HttpResponse("Payload successfully received")


        # Find the latest record for the current date with the matching device_eui in payload_power_mst
        # try:
        #     matching_dev = device_register_details.objects.get(dev_eui=devEUI)
        #     zone_nam=matching_dev.device_zone
        #     ward_nam=matching_dev.device_ward
        #     previous_date = current_date - timedelta(days=1)
        #     print(previous_date)
        #     previous_day_data = payload_power_mst.objects.filter(device_eui=devEUI).latest('date')
        #     print(previous_day_data)

        #     exists_powers=previous_day_data.power_consume
        #     print(exists_powers)
        #     new_power_consume=(float(total_kwhss)-float(exists_powers))
        #     print(new_power_consume)
        #     # total_new_kwh=new_power_consume + float(exists_powers)



        #     latest_power = payload_power_mst.objects.filter(device_eui=devEUI, date=current_date).latest('date')
        #     new_values = {
        #         'zone_name':zone_nam,
        #         'ward_name':ward_nam,
        #         'date': current_date,
        #         'device_on_off': on_off_status,
        #         'power_consume': new_power_consume,
        #     }

        #     # Update the latest record with the new values
        #     for field, value in new_values.items():
        #         setattr(latest_power, field, value)
        #     latest_power.save()
        #     print('Data updated successfully for Power')

        # except payload_power_mst.DoesNotExist:
        #     # If no record exists, create a new one in payload_power_mst
        #     matching_devs = device_register_details.objects.get(dev_eui=devEUI)
        #     exists_power=payload_power_mst.objects.filter(device_eui=devEUI).latest('date')
        #     total_power_except_current_date = payload_power_mst.objects.filter(
        #     device_eui=devEUI,
        #     date__lt=current_date  # Filter out records with dates less than the current date
        #     ).aggregate(total_power=Sum('power_consume'))['total_power']

        #     # If there are no records before the current date, set the total power to 0
        #     if total_power_except_current_date is None:
        #         total_power_except_current_date = 0

        #     print(total_power_except_current_date,'GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG')
        #     if exists_power:
        #         exists_powers=exists_power.power_consume
        #         print(exists_powers,'ffffffffffffff')
        #         new_power_consume=(float(total_kwhss)-float(total_power_except_current_date))
        #         print(new_power_consume)
            
        #         latest_power = payload_power_mst.objects.filter(device_eui=devEUI, date=current_date).latest('date')
        #         new_values = {
        #             'zone_name':zone_nam,
        #             'ward_name':ward_nam,
        #             'date': current_date,
        #             'device_on_off': on_off_status,
        #             'power_consume': new_power_consume,
        #         }
        #         for field, value in new_values.items():
        #             setattr(latest_power, field, value)
        #         latest_power.save()
        #         print('New data updated successfully for Power')

        #     else:
        #         matching_devs = device_register_details.objects.get(dev_eui=devEUI)
        #         create_new = payload_power_mst.objects.create(
        #             fk_device=matching_devs,
        #             device_eui=devEUI,
        #             power_consume=total_kwhss,
        #             date=current_date,
        #             device_on_off=on_off_status,
        #             zone_name=zone_nam,
        #             ward_name=ward_nam,
        #         )
        #         print('New record created and data saved successfully for Power')
        # return HttpResponse("Payload successfully received")
 
    elif str(ascii_value)=='L7':
        print('yes working for L7')
        dev_mode=new_pay[2]
        print(dev_mode)
        start_time=new_pay[3]
        print(start_time)
        hour = start_time[:2]
        minute = start_time[2:]
        start_timess = f"{hour}:{minute}:00"
        # time_obj=datetime.strptime(start_time, "%H%M")
        # start_timess=time_obj.strftime("%H:%M:%S")
        print(start_timess,'okkkk')

        end_time=new_pay[4]
        print(end_time)
        # time_obj=datetime.strptime(end_time, "%H%M")
        # end_timess=time_obj.strftime("%H:%M:%S")
        hour = end_time[:2]
        minute = end_time[2:]
        end_timess = f"{hour}:{minute}:00"

        print(end_timess)

        relay_on_off=new_pay[5]
        if relay_on_off=='1':
            relay_on_off='ON'
        else:
            relay_on_off='OFF'

        print(relay_on_off)

        dimming_value=new_pay[6]
        print(dimming_value)
 
        f_time=new_pay[7]
        print(f_time)

        # time_obj=datetime.strptime(f_time, "%H%M")
        # f_timess=time_obj.strftime("%H:%M:%S")
        hour = f_time[:2]
        minute = f_time[2:]
        f_timess = f"{hour}:{minute}:00"
        print(f_timess)

        f_dim=new_pay[8]
        print(f_dim)

        s_time=new_pay[9]
        print(s_time)

        # time_obj=datetime.strptime(s_time, "%H%M")
        # s_timess=time_obj.strftime("%H:%M:%S")

        hour = s_time[:2]
        minute = s_time[2:]
        s_timess = f"{hour}:{minute}:00"
        print(s_timess)

        s_dim=new_pay[10]
        print(s_dim)

    
        tr_time=str(new_pay[11])
        print(tr_time)
        hour = tr_time[:2]
        minute = tr_time[2:]
        tr_timess = f"{hour}:{minute}:00"
       

        # time_obj=datetime.strptime(tr_time, "%H%M")
        # tr_timess=time_obj.strftime("%H:%M:%S")
 
        print(tr_timess)

        tr_dim=new_pay[12]
        print(tr_dim)
 
        fo_time=str(new_pay[13])
        print(fo_time)
        # time_obj=datetime.strptime(fo_time, "%H%M")
        # fo_timess=time_obj.strftime("%H:%M:%S")

        hour = fo_time[:2]
        minute = fo_time[2:]
        fo_timess = f"{hour}:{minute}:00"
        print(fo_timess)

        fo_dim=new_pay[14].replace('*','')

        print(fo_dim)
        current_date = date.today()

        try:
            # Try to find the latest record for the current date with the matching devEUI
            latest_record = payloaddata.objects.filter(devEUI=devEUI, time_stamp__date=current_date).latest('time_stamp')

            # If a record exists, update the latest row
            latest_record.devEUI = devEUI
            latest_record.time_stamp = datetime.now()
            latest_record.relay_status = relay_on_off
            latest_record.sch_start_time = start_timess
            latest_record.sch_end_time = end_timess
            latest_record.default_dimming = dimming_value
            latest_record.first_slot_time = f_timess
            latest_record.first_slot_dimming = f_dim
            latest_record.second_slot_time = s_timess
            latest_record.second_slot_dimming = s_dim
            latest_record.third_slot_time = tr_timess
            latest_record.third_slot_dimming = tr_dim
            latest_record.fourth_slot_time = fo_timess
            latest_record.fourth_slot_dimming = fo_dim
            latest_record.save()
            print('Data updated successfully in payloaddata table for L7')

        except payloaddata.DoesNotExist:
            # If no record exists for the current date, create a new one
            matching_dev = device_register_details.objects.get(dev_eui=devEUI)
            post = payloaddata(
                device=matching_dev,
                devEUI=devEUI,
                time_stamp=datetime.now(),
                relay_status=relay_on_off,
                sch_start_time=start_timess,
                sch_end_time=end_timess,
                default_dimming=dimming_value,
                first_slot_time=f_timess,
                first_slot_dimming=f_dim,
                second_slot_time=s_timess,
                second_slot_dimming=s_dim,
                third_slot_time=tr_timess,
                third_slot_dimming=tr_dim,
                fourth_slot_time=fo_timess,
                fourth_slot_dimming=fo_dim
            )
            post.save()
            print('Data saved successfully in payloaddata table for L7')
                 
        return HttpResponse("payload successfully recived  ")
    else:
        print('Not Found')
        return HttpResponse("payload not in correct format")  

from utils import call_publish_cmd 
@csrf_exempt
@api_view(['GET', 'POST'])
def set_command(request, devEUI, command):
    if request.method == "GET":
        res = command
        devEUI = devEUI
        command = command
        print(command, 'cooooo')
        print(devEUI, 'devvvv')
        if str(command) == 'on':
            print('Received command for ON ')
            command = '4c337c312a'
            dev_cat=device_register_details.objects.get(dev_eui=devEUI)
            device_category = dev_cat.device_category
            ############# MQTT Call ###########################
            if str(device_category) == "4G":
                print("yes it is 4G device,i am call mqtt publish")

                response = call_publish_cmd(request,devEUI,command)
                print("yes call mqtt publish")
                print("Mqtt response:::",response)

                status_code = response.status_code
                print(status_code)
                if status_code == 200:
                    return Response("L3|0*")
                else:
                    return HttpResponse('Failed')

                ########### LoRa Call #################
            else:
                result = downlink_commands(devEUI, command)
                print('Downlink Send and sleep 8 sec')
                time.sleep(8)
                status_code = result.status_code
                status=device_status.get('response')
                if status_code == 200 and status is not None :
                    print('Yes, Got Uplink ')
                    clear_thread = threading.Thread(target=clear_response)
                    clear_thread.start()
                    clear_thread.join()
                    print('Temp data remove')
                    byte_value = bytes.fromhex(status)
                    # Convert the bytes to ASCII
                    ascii_value = byte_value.decode('ascii')
                    print('Sending Response......', ascii_value,)
                    return Response(ascii_value)
                else:
                    return HttpResponse('Failed')

        elif str(command) == 'off':
            print('Yes, working for off')
            command = '4c337c302a'
            dev_cat=device_register_details.objects.get(dev_eui=devEUI)
            device_category = dev_cat.device_category
            ############# MQTT Call ###########################
            if str(device_category) == "4G":
                print("yes it is 4G device,i am call mqtt publish")

                response = call_publish_cmd(request,devEUI,command)
                print("yes call mqtt publish")
                print("Mqtt response:::",response)
                status_code = response.status_code
                if status_code == 200:
                    return Response('off')
                else:
                    return HttpResponse('Failed')

                
                ########### LoRa Call #################
            else:
                result = downlink_commands(devEUI, command)
                time.sleep(8)
                status_code = result.status_code
                
                status=device_status.get('response')
                if status_code == 200 and status is not None :
                    print('Yes Got Uplink')
                    clear_thread = threading.Thread(target=clear_response)
                    clear_thread.start()
                    clear_thread.join()
                    print('Temp data remove')

                    byte_value = bytes.fromhex(status)
                    # Convert the bytes to ASCII
                    ascii_value = byte_value.decode('ascii')
                    print('Sending Response........',ascii_value)
                    return Response('off')
                else:
                    return HttpResponse('Failed')

        elif str(command) =='get':
            print('Received command for Get Data')
            hex_command = 'L5|*'
            command = ''.join([hex(ord(char))[2:] for char in hex_command])
            result = downlink_commands(devEUI, command)
            time.sleep(8)
            status_code = result.status_code
            
            status=device_status.get('response')
            if status_code == 200 and status is not None :

                print('Yes Got Uplink')
                clear_thread = threading.Thread(target=clear_response)
                clear_thread.start()
                clear_thread.join()
                print('Temp data remove')

                byte_value = bytes.fromhex(status)
                # Convert the bytes to ASCII
                ascii_value = byte_value.decode('ascii')
                print('Sending Response........',ascii_value)
                return Response(ascii_value)
            else:
                print('Failed')
                return Response("HTTP_400_BAD_REQUEST.............")

        elif str(command) =='meter':
            print('Received command for Get Meter Data')

            hex_command = 'L6|*'
            command = ''.join([hex(ord(char))[2:] for char in hex_command])
            result = downlink_commands(devEUI, command)
            time.sleep(8)
            status_code = result.status_code
            
            status=device_status.get('response')
            if status_code == 200 and status is not None :
                print('Yes Got Uplink')
                clear_thread = threading.Thread(target=clear_response)
                clear_thread.start()
                clear_thread.join()
                print('Temp data remove')
                byte_value = bytes.fromhex(status)
                # Convert the bytes to ASCII
                ascii_value = byte_value.decode('ascii')
                print('Sending Response........',ascii_value)
                return Response(ascii_value)
            else:
                return HttpResponse('Failed')

        elif str(command) =='rtc':
            print('Received command for RTC')
            hex_command = 'LA|*'
            command = ''.join([hex(ord(char))[2:] for char in hex_command])
            result = downlink_commands(devEUI, command)
            time.sleep(8)
            status_code = result.status_code
            
            status=device_status.get('response')
            if status_code == 200 and status is not None :
                print('Yes Got Uplink')
                clear_thread = threading.Thread(target=clear_response)
                clear_thread.start()
                clear_thread.join()
                print('Temp data remove')

                byte_value = bytes.fromhex(status)
                # Convert the bytes to ASCII
                ascii_value = byte_value.decode('ascii')
                print('Sending Response........',ascii_value)
                return Response(ascii_value)
            else:
                return HttpResponse('Failed')
        elif str(command) =='schedule':
            print('Received command for Schedule Data')
            hex_command = 'L7|*'
            command = ''.join([hex(ord(char))[2:] for char in hex_command])
            result = downlink_commands(devEUI, command)
            time.sleep(8)
            status_code = result.status_code
            
            status=device_status.get('response')
            if status_code == 200 and status is not None :
                print('Yes Got Uplink')
                clear_thread = threading.Thread(target=clear_response)
                clear_thread.start()
                clear_thread.join()
                print('Temp data remove')

                byte_value = bytes.fromhex(status)
                # Convert the bytes to ASCII
                ascii_value = byte_value.decode('ascii')
                print('Sending Response........',ascii_value)
                return Response(ascii_value)
            else:
                return HttpResponse('Failed')

        else:
            return Response('HTTP_400_BAD_REQUEST.............')
    else:
        return Response("HTTP_400_BAD_REQUEST.............")

   # Replace with the actual import for your gRPC module

def device_downlinkv4(dev_eui,command):
    if request.method == 'GET':
        dev_eui =  dev_eui
        command =  command

        print('set default global parameter')
        lora_login_url = "http://gcp.siotel.in"
        username = "admin"
        password = "admin"
        test_data = []

        for i in range(0, len(command), 2):
            print(i)
            p = i + 2
            z = command[i:p]
            a = int(z, base=16)
            print(a)

            if len(str(z)) != 2:
                z = str(z).zfill(2)
            else:
                z = a
                test_data.append(z)

        print(test_data)
        server = "gcp.siotel.in:8080"
        api_token = "your_api_token_here"  # Replace with your actual API token

        channel = grpc.insecure_channel(server)
        client = api.DeviceServiceStub(channel)
        auth_token = [("authorization", "Bearer %s" % api_token)]
        req = api.EnqueueDeviceQueueItemRequest()
        req.queue_item.confirmed = False
        req.queue_item.data = bytes(test_data)
        req.queue_item.dev_eui = dev_eui
        req.queue_item.f_port = 10
        resp = client.Enqueue(req, metadata=auth_token)
        print('55555555555555555555555555555555')
        print(resp)
        return HttpResponse("Okk Downlink send............................................. ")
    return HttpResponse("Unsupported HTTP method")
 
class SupportAPI(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        if request.method == "POST":  # You can change this to if request.method == "POST":
            print("Yes",request.data)
            serializer = SupportSerializer(data=request.data)
            if serializer.is_valid( ):
                print('yes')
                serializer.save()
                print('Save')
                return Response('success', status=status.HTTP_201_CREATED)
            else:
                return Response('Not validated', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Method Not Allowed', status=status.HTTP_400_BAD_REQUEST)



######################################  Send Email ########################################
# def sendemail(email):

#     sender_email = "charulgarg09@gmail.com"
#     receiver_email = email
#     password = "iglofesxaxykligq"
#     subject = "Test Email"
#     body = "Thank you for your efforts, we got your Complaint"
#     body1="your reference id is "
#     token=generateOTP()
#     message = f"Subject: {subject}\n\n{body}\n\n{body1}\n\n{token}"
#     with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
#         smtp.starttls()
#         smtp.login(sender_email, password)
#         smtp.sendmail(sender_email, receiver_email, message)