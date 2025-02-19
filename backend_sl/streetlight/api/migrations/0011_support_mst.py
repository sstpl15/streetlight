# Generated by Django 4.2.5 on 2023-10-13 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_site_manager_site_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='support_mst',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requester_name', models.CharField(max_length=100)),
                ('requester_email', models.EmailField(max_length=254)),
                ('requester_number', models.IntegerField()),
                ('issue_details', models.TextField()),
            ],
        ),
    ]
