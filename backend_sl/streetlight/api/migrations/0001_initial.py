# Generated by Django 4.2.5 on 2023-09-11 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BulkFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='files')),
            ],
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_complaint', models.DateTimeField()),
                ('requester_name', models.CharField(max_length=100)),
                ('requester_designation', models.CharField(max_length=50)),
                ('device_eui', models.CharField(max_length=20)),
                ('device_zone', models.CharField(max_length=30)),
                ('device_pole_no', models.IntegerField()),
                ('device_ward', models.CharField(max_length=20)),
                ('issue_details', models.TextField()),
                ('complaint_number', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='device_register_details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dev_eui', models.CharField(max_length=50, unique=True)),
                ('device_zone', models.CharField(max_length=50)),
                ('device_ward', models.CharField(max_length=50)),
                ('pol_number', models.CharField(max_length=50)),
                ('device_watt', models.IntegerField()),
                ('device_type', models.CharField(max_length=50)),
                ('device_latitude', models.CharField(max_length=20)),
                ('device_longitude', models.CharField(max_length=20)),
                ('dev_reg_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='uplinkdata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deveui', models.CharField(max_length=50)),
                ('time_stamp', models.DateTimeField()),
                ('gateway_mac', models.CharField(max_length=50)),
                ('frequency', models.IntegerField()),
                ('applicationName', models.CharField(max_length=100)),
                ('dataRate', models.CharField(max_length=50)),
                ('spreadingFactor', models.CharField(max_length=20)),
                ('fCnt', models.CharField(max_length=20)),
                ('rssi', models.CharField(max_length=20)),
                ('snr', models.IntegerField()),
                ('payload', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='user_registartion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('phone_no', models.CharField(max_length=12)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.CharField(max_length=255)),
                ('zone_name', models.CharField(max_length=255)),
                ('designation', models.CharField(max_length=255)),
                ('area_code', models.IntegerField()),
                ('login_user_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Ward_details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone_name', models.CharField(max_length=50)),
                ('ward_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Zone_details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='payloaddata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('devEUI', models.CharField(max_length=100)),
                ('dev_status', models.CharField(max_length=20)),
                ('luc_detail', models.CharField(max_length=50)),
                ('schedule_mode', models.CharField(max_length=50)),
                ('relay_status', models.CharField(max_length=100)),
                ('power_grid_fail', models.CharField(max_length=100)),
                ('lamp_fali', models.CharField(max_length=100)),
                ('command_action_status', models.CharField(max_length=100)),
                ('time_stamp', models.DateTimeField()),
                ('sch_start_time', models.TimeField()),
                ('sch_end_time', models.TimeField()),
                ('default_dimming', models.IntegerField()),
                ('first_slot_time', models.TimeField()),
                ('first_slot_dimming', models.IntegerField()),
                ('second_slot_time', models.TimeField()),
                ('second_slot_dimming', models.IntegerField()),
                ('third_slot_time', models.TimeField()),
                ('third_slot_dimming', models.IntegerField()),
                ('fourth_slot_time', models.TimeField()),
                ('fourth_slot_dimming', models.IntegerField()),
                ('meter_data_interval', models.IntegerField()),
                ('current_dimming', models.FloatField()),
                ('meter_kwh', models.FloatField()),
                ('meter_voltage', models.FloatField()),
                ('meter_current', models.FloatField()),
                ('latitude', models.CharField(max_length=20)),
                ('longitude', models.CharField(max_length=20)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.device_register_details')),
            ],
        ),
        migrations.CreateModel(
            name='payload_power_mst',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_eui', models.CharField(max_length=20)),
                ('zone_name', models.CharField(max_length=50)),
                ('ward_name', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('power_consume', models.CharField(max_length=100)),
                ('power_save', models.CharField(max_length=100)),
                ('device_on_off', models.CharField(max_length=20)),
                ('fk_device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.device_register_details')),
            ],
        ),
        migrations.CreateModel(
            name='maintenance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_eui', models.CharField(max_length=100)),
                ('date_of_inspection', models.DateTimeField()),
                ('inspector_name', models.CharField(max_length=100)),
                ('device_latitude', models.CharField(max_length=20)),
                ('device_longitude', models.CharField(max_length=20)),
                ('device_pole_no', models.IntegerField()),
                ('device_zone', models.CharField(max_length=20)),
                ('check_choice', models.CharField(max_length=20)),
                ('cleaned_choice', models.CharField(max_length=20)),
                ('repaired_choice', models.CharField(max_length=20)),
                ('device_replace', models.CharField(max_length=10)),
                ('maintenance_status', models.CharField(max_length=20)),
                ('issue_details', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='images')),
                ('complaint_number', models.CharField(max_length=20, null=True)),
                ('complaint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.complaint')),
            ],
        ),
    ]
