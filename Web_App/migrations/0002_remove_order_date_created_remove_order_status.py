# Generated by Django 4.1 on 2022-09-01 19:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Web_App', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='order',
            name='status',
        ),
    ]
