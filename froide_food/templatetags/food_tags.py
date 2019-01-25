from django import template

register = template.Library()


@register.filter
def request_population_ratio(value):
    if isinstance(value, dict):
        req = value['request_count']
        pop = value['population']
    else:
        req = value.request_count
        pop = value.population
    return round(req / pop * 100_000, 1)


@register.filter
def in_mio(value):
    return round(value / 1_000_000, 2)
