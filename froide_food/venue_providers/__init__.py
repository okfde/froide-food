from .google import GoogleVenueProvider
from .yelp import YelpVenueProvider


venue_providers = {
    'google': GoogleVenueProvider(),
    'yelp': YelpVenueProvider(),
}

venue_provider = venue_providers['yelp']
