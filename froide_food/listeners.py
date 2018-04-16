from .models import VenueRequest


def connect_request_object(sender, **kwargs):
    reference = kwargs.get('reference')
    if not reference:
        return
    if not reference.startswith('food:'):
        return
    namespace, food_place_id = reference.split(':', 1)

    VenueRequest.objects.create(
        ident=food_place_id,
        name=sender.title,
        foirequest=sender,
        publicbody=sender.public_body
    )
