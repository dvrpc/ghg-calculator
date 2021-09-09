"""
Bokeh apps are served up independently of this Django app, using the `bokeh serve` command. In
production, that means that systemd service files are created for each bokeh app, and then nginx
locations are used to proxy them to the appropriate path. Below, in the calls to
`server_document`, that end of that nginx location url is used (with any path between it and
the domain set in `url_prefix`.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bokeh.embed import server_document

url_prefix = "/app/ghg/"  # path after domain where the app lives


def index(request):
    return render(request, "main/intro.html")


def pop(request: HttpRequest) -> HttpResponse:
    script = server_document(url_prefix + "bokeh-pop", relative_urls=True)
    return render(request, "main/pop.html", dict(script=script))


def electricity_grid(request: HttpRequest) -> HttpResponse:
    script = server_document(url_prefix + "bokeh-grid", relative_urls=True)
    return render(request, "main/grid.html", dict(script=script))


def res_stationary(request: HttpRequest) -> HttpResponse:
    script = server_document(url_prefix + "bokeh-res", relative_urls=True)
    return render(request, "main/res.html", dict(script=script))


def non_res_stationary(request: HttpRequest) -> HttpResponse:
    script = server_document(url_prefix + "bokeh-non-res", relative_urls=True)
    return render(request, "main/non_res.html", dict(script=script))


def on_road_motor_veh(request: HttpRequest) -> HttpResponse:
    script = server_document(url_prefix + "bokeh-on-road", relative_urls=True)
    return render(request, "main/on_road.html", dict(script=script))


def rail(request: HttpRequest) -> HttpResponse:
    script = server_document(url_prefix + "bokeh-rail", relative_urls=True)
    return render(request, "main/rail.html", dict(script=script))


def aviation(request: HttpRequest) -> HttpResponse:
    script = server_document(url_prefix + "bokeh-aviation", relative_urls=True)
    return render(request, "main/aviation.html", dict(script=script))


def mobile_other(request: HttpRequest) -> HttpResponse:
    script = server_document(url_prefix + "bokeh-other", relative_urls=True)
    return render(request, "main/other.html", dict(script=script))


def non_energy(request: HttpRequest) -> HttpResponse:
    script = server_document(url_prefix + "bokeh-non-energy", relative_urls=True)
    return render(request, "main/non_energy.html", dict(script=script))


def sequestration_storage(request: HttpRequest) -> HttpResponse:
    script = server_document(url_prefix + "bokeh-seq", relative_urls=True)
    return render(request, "main/seq.html", dict(script=script))
