# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-07 14:18
from __future__ import unicode_literals

from django.db import migrations


def move_to_request_item(apps, schema_editor):
    VenueRequest = apps.get_model("froide_food", "VenueRequest")
    VenueRequestItem = apps.get_model("froide_food", "VenueRequestItem")

    for venue in VenueRequest.objects.all():
        VenueRequestItem.objects.create(
            venue=venue,
            foirequest=venue.foirequest,
            timestamp=venue.timestamp,
            publicbody=venue.publicbody,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("froide_food", "0003_venuerequestitem"),
    ]

    operations = [
        migrations.RunPython(move_to_request_item),
    ]
