# Generated by Django 5.2 on 2025-05-31 05:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stadium_booking', '0002_alter_add_stadium_gst_percent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stadiumbooking',
            name='end_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='stadiumbooking',
            name='extra_charges',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
