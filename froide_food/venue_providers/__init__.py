from .base import VenueProviderException
from .google import GoogleVenueProvider
from .yelp import YelpVenueProvider
from .foursquare import FoursquareVenueProvider
from .custom import CustomVenueProvider

__all__ = ['VenueProviderException', 'venue_provider', 'venue_providers']

venue_providers = {
    'google': GoogleVenueProvider(),
    'yelp': YelpVenueProvider(),
    'foursquare': FoursquareVenueProvider(),
    'custom': CustomVenueProvider()
}

venue_provider = venue_providers['google']
