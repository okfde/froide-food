# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-10 08:39
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("froide_food", "0007_auto_20180618_1217"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="venuerequestitem",
            options={
                "ordering": ("-timestamp",),
                "verbose_name": "Venue Request Item",
                "verbose_name_plural": "Venue Requests Items",
            },
        ),
        migrations.AlterField(
            model_name="venuerequestitem",
            name="venue",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="request_items",
                to="froide_food.VenueRequest",
            ),
        ),
    ]
