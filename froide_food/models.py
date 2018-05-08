from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField

from froide.publicbody.models import PublicBody
from froide.foirequest.models import FoiRequest


class VenueRequest(models.Model):
    ident = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=1000)

    context = JSONField(blank=True, default=dict)

    timestamp = models.DateTimeField(auto_now=True)

    publicbody = models.ForeignKey(PublicBody, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    foirequest = models.ForeignKey(FoiRequest, null=True, blank=True,
                                   on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('Venue Request')
        verbose_name_plural = _('Venue Requests')

    def __str__(self):
        return self.name
