# Generated by Django 4.2.5 on 2023-09-29 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_site_manager_site_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='site_manager',
            name='server_name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
