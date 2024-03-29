import functools
import json
import operator
from collections import Counter, defaultdict

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, F, OuterRef, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt

from froide.foirequest.views import MakeRequestView
from froide.georegion.models import GeoRegion
from froide.helper.utils import get_redirect, is_ajax, render_403

from .forms import ReportForm
from .models import VenueRequest, VenueRequestItem
from .utils import (
    MAX_REQUEST_COUNT,
    get_all_food_safety_agencies,
    get_city_from_request,
    get_hygiene_publicbody,
    get_request_count,
    make_request_url,
)
from .venue_providers import venue_provider, venue_providers


def get_food_map_config(request, embed):
    city = get_city_from_request(request)

    return {
        "city": city or {},
        "filters": venue_provider.FILTERS,
        "embed": embed,
        "requestUrl": "{}{}".format(settings.SITE_URL, reverse("food-make_request")),
        "staticUrl": settings.STATIC_URL,
        "appUrl": settings.SITE_URL + reverse("food-index"),
        # "swUrl": reverse("food-service_worker"),
    }


def index(request, base_template="froide_food/base.html", embed=False):

    fake_make_request_view = MakeRequestView(request=request)

    context = {
        "base_template": base_template,
        "config": json.dumps(get_food_map_config(request, embed)),
        "request_form": fake_make_request_view.get_form(),
        "user_form": fake_make_request_view.get_user_form(),
        "request_config": json.dumps(fake_make_request_view.get_js_context()),
    }

    return render(request, "froide_food/index.html", context)


@xframe_options_exempt
def embed(request):
    return index(request, base_template="froide_food/embed_base.html", embed=True)


def make_request(request):
    ident = request.GET.get("ident")
    if not ident:
        messages.add_message(request, messages.ERROR, "Fehlerhafter Link")
        return redirect("food-index")
    try:
        provider, _ = ident.split(":")
        if provider not in venue_providers:
            raise ValueError
    except ValueError:
        messages.add_message(request, messages.ERROR, "Fehlerhafter Link")
        return redirect("food-index")

    place = venue_providers[provider].get_place(ident)
    if place is None:
        return redirect("food-index")

    return get_redirect(
        request,
        default="food-index",
        params={
            "query": place["name"],
            "latlng": "{},{}".format(place["lat"], place["lng"]),
            "ident": ident,
        },
    )


def old_make_request(request, place, ident):
    try:
        pb = get_hygiene_publicbody(place["lat"], place["lng"])
    except ValueError as e:
        messages.add_message(request, messages.ERROR, str(e))
        return redirect("food-index")

    url = make_request_url(place, pb)

    stopper = False
    request_count = 0
    if request.user.is_authenticated:
        request_count = get_request_count(request, pb)
        if request_count >= MAX_REQUEST_COUNT:
            stopper = True

    if stopper or request.GET.get("stopper") is not None:
        return get_redirect(
            request,
            default="food-index",
            params={
                "query": place["name"],
                "latlng": "{},{}".format(place["lat"], place["lng"]),
                "ident": ident,
            },
        )

    return redirect(url)


def osm_help(request):
    vrs = VenueRequest.objects.exclude(
        ident__startswith="amenity", context__checked=True
    )
    if request.method == "POST":
        ACTIONS = ("osmfixed", "notexist", "shouldwork", "osmmissing")
        venue_id = request.POST.get("venue_id")
        action = request.POST.get("action")

        if action in ACTIONS:
            try:
                venue = vrs.get(id=venue_id)
                venue.context.update(
                    {
                        "checked": True,
                        "action": action,
                        "osmid": request.POST.get("osmid"),
                    }
                )
                venue.save()
            except VenueRequest.DoesNotExist:
                pass
        if is_ajax(request):
            return JsonResponse({})
        return redirect("food-osm_help")

    city = request.GET.get("city")
    if city:
        city_q = functools.reduce(
            operator.and_, [Q(address__contains=c.strip()) for c in city.split()]
        )
        vrs = vrs.filter(city_q)

    vrs = vrs.order_by("?")[:30]
    return render(
        request, "froide_food/osm_help.html", {"venues": vrs, "city": city or ""}
    )


def requests_in_region(request, slug):
    region = get_object_or_404(GeoRegion, slug=slug)

    regions = region.get_descendants()
    pbs = (
        get_all_food_safety_agencies()
        .filter(regions__in=regions)
        .distinct()
        .prefetch_related("regions")
    )
    vris = VenueRequestItem.objects.filter(
        publicbody__in=pbs, timestamp__year__gte=2019
    )
    total = vris.count()
    by_region = Counter(vris.values_list("publicbody_id", flat=True))
    pb_map = defaultdict(list)

    for pb in pbs:
        pb.request_count = by_region[pb.id]
        r = pb.regions.all()[0]
        pb.region = r
        pb.center = r.geom.centroid

    for vri in vris.select_related("venue"):
        pb_map[vri.publicbody_id].append(vri)
    for pb in pbs:
        pb.requests = pb_map[pb.id]

    pbs = sorted(pbs, key=lambda x: x.request_count, reverse=True)

    return render(
        request,
        "froide_food/by_regions.html",
        {
            "region": region,
            "total": total,
            "pbs": pbs,
            "vris": vris,
            "center": region.geom.centroid,
        },
    )


def stats(request):

    base_stats = dict(
        request_count=Count("*"),
        user_count=Count("foirequest__user_id", distinct=True),
    )

    def agg_requests(qs, **extras):
        return qs.annotate(**base_stats, **extras).order_by("-request_count")

    city_states = ("Berlin", "Hamburg", "Bremen")
    city_regions = GeoRegion.objects.filter(
        kind__in=("borough", "district"),
        part_of__name__in=city_states,
    )
    top_regions_raw = GeoRegion.objects.exclude(name__in=city_states).filter(
        population__isnull=False, kind="district", kind_detail__contains="Stadt"
    )
    REGION_COUNT = 50
    top_regions = top_regions_raw.order_by("-population")[:REGION_COUNT]

    top_regions = GeoRegion.objects.filter(
        id__in=[t.id for t in top_regions] + [t.id for t in city_regions]
    ).select_related("part_of")

    vris = VenueRequestItem.objects.exclude(
        foirequest__status="awaiting_user_confirmation",
    ).filter(timestamp__year__gte=2019, foirequest__isnull=False)
    total = vris.aggregate(**base_stats)

    by_jurisdiction = agg_requests(
        vris.annotate(
            population=F("publicbody__jurisdiction__region__population")
        ).values("publicbody__jurisdiction__name", "population"),
    )

    by_region = top_regions.annotate(
        request_count=Count(
            "publicbody__venuerequestitem",
            filter=Q(publicbody__venuerequestitem__in=vris),
            distinct=True,
        ),
        user_count=Count(
            "publicbody__venuerequestitem__foirequest__user_id",
            filter=Q(publicbody__venuerequestitem__in=vris),
            distinct=True,
        ),
    )
    regions = {}
    for top in by_region:
        if top.part_of.name in city_states:
            name = top.part_of.name
            regions.setdefault(name, {"population": top.part_of.population})
            region = regions[name]
        else:
            name = top.name
            region = {"population": top.population}
            regions[name] = region
        region["name"] = name
        region.setdefault("request_count", 0)
        region["request_count"] += top.request_count
        region.setdefault("user_count", 0)
        region["user_count"] += top.user_count

    regions = list(regions.values())

    # Special case SH
    sh_regions = (
        GeoRegion.objects.filter(
            population__isnull=False,
            kind="district",
            kind_detail__contains="Stadt",
            part_of__name="Schleswig-Holstein",
        )
    ).order_by("-population")[:5]
    small_regions = GeoRegion.objects.filter(
        Q(name="Hannover", kind="municipality")
        | Q(name="Saarbrücken", kind="municipality")
    )
    sh_regions = GeoRegion.objects.filter(
        id__in=[r.id for r in sh_regions] + [r.id for r in small_regions]
    )
    sh_query = functools.reduce(
        operator.or_, [Q(venue__geo__coveredby=x.geom) for x in sh_regions]
    )
    sh_vris = (
        vris.filter(sh_query)
        .annotate(
            region=Subquery(
                sh_regions.filter(geom__covers=OuterRef("venue__geo")).values("name")[
                    :1
                ]
            )
        )
        .select_related("venue", "foirequest")
    )

    region_map = {}
    for vri in sh_vris:
        for reg in sh_regions:
            if not reg.geom.covers(vri.venue.geo):
                continue
            if reg.name not in region_map:
                region = {
                    "name": reg.name,
                    "population": reg.population,
                    "request_count": 0,
                    "user_count": 0,
                    "region_users": set(),
                }
                region_map[reg.name] = region
            else:
                region = region_map[reg.name]
            region["request_count"] += 1
            if vri.foirequest.user_id not in region["region_users"]:
                region["user_count"] += 1
            region["region_users"].add(vri.foirequest.user_id)
            break

    regions = regions + list(region_map.values())
    regions = list(sorted(regions, key=lambda x: x["request_count"], reverse=True))[
        :REGION_COUNT
    ]

    return render(
        request,
        "froide_food/stats.html",
        {
            "total": total,
            "now": timezone.now(),
            "by_jurisdiction": by_jurisdiction,
            "by_region": regions,
        },
    )


def show_reports(request):
    if not request.user.is_authenticated:
        return render_403(request)
    if not request.user.has_perm("froide_food.add_foodsafetyreport"):
        return render_403(request)

    if is_ajax(request):
        if request.method == "GET":
            vri = VenueRequestItem.objects.filter(
                Q(foirequest__resolution="successful")
                | Q(foirequest__resolution="partially_successful"),
                foirequest__status="resolved",
                checked_date__isnull=True,
            ).order_by("?")[:1]
            if not vri:
                return JsonResponse({"foirequest": None})
            return JsonResponse({"foirequest": vri[0].foirequest_id})
        data = json.loads(request.body.decode("utf-8"))
        form = ReportForm(data=data)
        if form.is_valid():
            form.save()
        return JsonResponse({"errors": None})

    return render(request, "froide_food/report.html")
