from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.gis.geos import Point

from django_amenities.models import Amenity
from dateutil.relativedelta import relativedelta

from froide.publicbody.models import PublicBody
from froide.foirequest.models import FoiRequest, FoiMessage, FoiAttachment


REPORT_ALLOWED_AGE = relativedelta(years=5)


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

    context = models.JSONField(blank=True, default=dict)
    amenity = models.ForeignKey(
        Amenity, null=True, blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _('Venue Request')
        verbose_name_plural = _('Venue Requests')

    def __str__(self):
        return self.name

    def update_from_items(self):
        vris = VenueRequestItem.objects.filter(venue=self)

        if vris:
            vri = vris[0]
            self.last_request = vri.timestamp
            if vri.foirequest:
                self.last_status = vri.foirequest.status
                self.last_resolution = vri.foirequest.resolution
            self.save()
        else:
            self.last_request = None
            self.last_status = ''
            self.last_resolution = ''
            self.save()

    def to_place(self, with_requests=False):
        d = {
            'ident': self.ident,
            'lat': self.geo.coords[1] if self.geo else None,
            'lng': self.geo.coords[0] if self.geo else None,
            'name': self.name,
            'address': self.address,
            'requests': [],
            'custom': self.ident.startswith('custom:')
        }
        if with_requests:
            d.update({
                'last_status': self.last_status,
                'last_resolution': self.last_resolution,
                'last_request': self.last_request,
            })
            fr = self.last_request
            if fr is not None:
                vris = self.request_items.all()
                d['requests'] = [vri.to_request() for vri in vris]
        return d

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
        if place['address']:
            self.address = place['address']
        if place['lng']:
            self.geo = Point(place['lng'], place['lat'])
        if place['name']:
            self.name = place['name']
        if not self.amenity and provider.name == 'amenity':
            self.amenity = provider.get_object(self.ident)


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
    checked_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = _('Venue Request Item')
        verbose_name_plural = _('Venue Requests Items')

    def __str__(self):
        return '%s %s' % (self.venue, self.timestamp)

    def to_request(self):
        if not self.foirequest:
            return {
                'id': None,
                'url': '',
                'status': '',
                'resolution': '',
                'timestamp': None,
                'documents': []
            }
        if self.foirequest.is_public():
            return {
                'id': self.foirequest.pk,
                'url': self.foirequest.get_absolute_url(),
                'status': self.foirequest.status,
                'resolution': self.foirequest.resolution,
                'timestamp': self.timestamp,
                'documents': []
            }
        return {
            'id': None,
            'url': '',
            'status': self.foirequest.status,
            'resolution': self.foirequest.resolution,
            'timestamp': self.timestamp,
            'documents': []
        }


class FoodSafetyReportManager(models.Manager):
    def get_expired_reports(self):
        now = timezone.now()
        ago = now - REPORT_ALLOWED_AGE

        return self.filter(complaints=True, date__lt=ago)


class FoodSafetyReport(models.Model):
    venue = models.ForeignKey(
        VenueRequest, null=True,
        on_delete=models.SET_NULL
    )
    request_item = models.ForeignKey(
        VenueRequestItem, null=True,
        on_delete=models.SET_NULL
    )

    message = models.ForeignKey(
        FoiMessage, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    attachment = models.ForeignKey(
        FoiAttachment, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    amenity = models.ForeignKey(
        Amenity, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    date = models.DateField(blank=True)
    complaints = models.BooleanField(default=False)
    disgusting = models.BooleanField(default=False)
    summary = models.TextField(blank=True)

    objects = FoodSafetyReportManager()

    class Meta:
        verbose_name = _('food safety report')
        verbose_name_plural = _('food safety reports')

    def __str__(self):
        return '{} - {}'.format(self.venue, self.date)


class FoodAuthorityStatus(models.Model):
    publicbodies = models.ManyToManyField(PublicBody)
    cooperative = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _('food authority status')
        verbose_name_plural = _('food authority stati')

    def __str__(self):
        return self.title
