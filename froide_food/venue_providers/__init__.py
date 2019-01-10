from .base import VenueProviderException
from .google import GoogleVenueProvider
from .yelp import YelpVenueProvider
from .custom import CustomVenueProvider

__all__ = ['VenueProviderException', 'venue_provider', 'venue_providers']

venue_providers = {
    'google': GoogleVenueProvider(),
    'yelp': YelpVenueProvider(),
    'custom': CustomVenueProvider()
}

venue_provider = venue_providers['yelp']
