from django.utils import timezone

from .models import VenueRequest, VenueRequestItem


def connect_request_object(sender, **kwargs):
    reference = kwargs.get('reference')
    if not reference:
        return
    if not reference.startswith('food:'):
        return
    namespace, food_place_id = reference.split(':', 1)

    venue, _ = VenueRequest.objects.get_or_create(
        ident=food_place_id,
        defaults={
            'name': sender.title,
            'last_request': timezone.now(),
            'last_status': 'awaiting_response'
        }
    )
    VenueRequestItem.objects.create(
        venue=venue,
        foirequest=sender,
        publicbody=sender.public_body
    )


def connect_request_status_changed(sender, **kwargs):
    if not sender.reference.startswith('food:'):
        return

    data = kwargs.pop('data', None)
    if data is None:
        return

    status = kwargs['status']
    vris = VenueRequestItem.objects.filter(foirequest=sender).select_related()
    for vri in vris:
        venue = vri.venue
        venue.last_status = status
        venue.last_request = sender.last_message
        venue.save()
