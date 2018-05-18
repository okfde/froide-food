from .base import VenueProviderException
from .google import GoogleVenueProvider
from .yelp import YelpVenueProvider

__all__ = ['VenueProviderException', 'venue_provider', 'venue_providers']

venue_providers = {
    'google': GoogleVenueProvider(),
    'yelp': YelpVenueProvider(),
}

venue_provider = venue_providers['yelp']
