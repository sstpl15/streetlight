# Generated by Django 4.1.3 on 2024-10-22 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='last_logout',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
