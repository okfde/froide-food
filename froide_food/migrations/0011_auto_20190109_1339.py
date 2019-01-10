# Generated by Django 2.1.4 on 2019-01-09 12:39

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_food', '0010_auto_20181008_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='venuerequest',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='venuerequest',
            name='geo',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326),
        ),
    ]