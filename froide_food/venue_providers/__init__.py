from .base import VenueProviderException
from .google import GoogleVenueProvider
from .yelp import YelpVenueProvider
from .foursquare import FoursquareVenueProvider
from .custom import CustomVenueProvider
from .amenity import AmenityVenueProvider
from .requested import RequestedVenueProvider

__all__ = ['VenueProviderException', 'venue_provider', 'venue_providers']

venue_providers = {
    'google': GoogleVenueProvider(),
    'yelp': YelpVenueProvider(),
    'foursquare': FoursquareVenueProvider(),
    'custom': CustomVenueProvider(),
    'amenity': AmenityVenueProvider(),
    'requested': RequestedVenueProvider(),
}

venue_provider = venue_providers['amenity']
