# Generated by Django 4.2.5 on 2023-09-26 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_payloaddata_command_action_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payload_power_mst',
            name='power_save',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='payload_power_mst',
            name='ward_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='payload_power_mst',
            name='zone_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
