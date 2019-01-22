from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from django.contrib.gis.geos import Point

from froide.publicbody.models import PublicBody
from froide.foirequest.models import FoiRequest


class VenueRequest(models.Model):
    ident = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=1000)

    last_request = models.DateTimeField(
        null=True, blank=True
    )
    last_status = models.CharField(max_length=50, blank=True)
    last_resolution = models.CharField(max_length=50, blank=True)

    address = models.TextField(blank=True)
    geo = models.PointField(null=True, blank=True, geography=True)

    context = JSONField(blank=True, default=dict)

    class Meta:
        verbose_name = _('Venue Request')
        verbose_name_plural = _('Venue Requests')

    def __str__(self):
        return self.name

    def to_place(self):
        return {
            'ident': self.ident,
            'lat': self.geo.coords[1] if self.geo else None,
            'lng': self.geo.coords[0] if self.geo else None,
            'name': self.name,
            'address': self.address,
            'requests': [],
            'custom': self.ident.startswith('custom:')
        }

    def get_provider(self):
        return self.ident.split(':', 1)[0]

    def get_venue_provider(self):
        from .venue_providers import venue_providers
        provider = self.get_provider()
        return venue_providers[provider]

    def update_from_provider(self):
        provider = self.get_venue_provider()
        if self.address and self.geo:
            return
        place = provider.get_place(self.ident)
        if place is None:
            return
        if not self.address:
            self.address = place['address']
        if not self.geo:
            self.geo = Point(place['lng'], place['lat'])
        if place['name']:
            self.name = place['name']


class VenueRequestItem(models.Model):
    venue = models.ForeignKey(
        VenueRequest, related_name='request_items',
        on_delete=models.CASCADE
    )

    timestamp = models.DateTimeField(default=timezone.now)
    foirequest = models.ForeignKey(FoiRequest, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    publicbody = models.ForeignKey(PublicBody, null=True, blank=True,
                                   on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = _('Venue Request Item')
        verbose_name_plural = _('Venue Requests Items')

    def __str__(self):
        return '%s %s' % (self.venue, self.timestamp)
