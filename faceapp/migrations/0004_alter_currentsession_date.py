# Generated by Django 4.0 on 2022-01-20 14:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faceapp', '0003_alter_currentsession_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currentsession',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
