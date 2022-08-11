from .amenity import AmenityVenueProvider
from .base import VenueProviderException
from .custom import CustomVenueProvider
from .foursquare import FoursquareVenueProvider
from .google import GoogleVenueProvider
from .requested import RequestedVenueProvider
from .yelp import YelpVenueProvider

__all__ = ["VenueProviderException", "venue_provider", "venue_providers"]

venue_providers = {
    "google": GoogleVenueProvider(),
    "yelp": YelpVenueProvider(),
    "foursquare": FoursquareVenueProvider(),
    "custom": CustomVenueProvider(),
    "amenity": AmenityVenueProvider(),
    "requested": RequestedVenueProvider(),
}

venue_provider = venue_providers["amenity"]
