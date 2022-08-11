from django import template

from ..models import FoodAuthorityStatus

register = template.Library()


@register.filter
def request_population_ratio(value):
    if isinstance(value, dict):
        req = value["request_count"]
        pop = value["population"]
    else:
        req = value.request_count
        pop = value.population
    return round(req / pop * 100_000, 1)


@register.filter
def in_mio(value):
    return round(value / 1_000_000, 2)


@register.inclusion_tag("froide_food/_authority_status.html")
def food_authority_status(foirequest):
    try:
        food_authority_status = FoodAuthorityStatus.objects.get(
            publicbodies=foirequest.public_body
        )
    except FoodAuthorityStatus.DoesNotExist:
        return {}
    return {"food_authority_status": food_authority_status}
