from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bokeh.embed import server_document

from environment import bokeh_base_url, relative_urls

url_prefix = "/app/ghg"


def index(request):
    return render(request, "main/intro.html")


def pop(request: HttpRequest) -> HttpResponse:
    script = server_document(
        bokeh_base_url + url_prefix + "/bokeh_pop", relative_urls=relative_urls
    )
    return render(request, "main/pop.html", dict(script=script))


def electricity_grid(request: HttpRequest) -> HttpResponse:
    script = server_document(
        bokeh_base_url + url_prefix + "/bokeh_grid", relative_urls=relative_urls
    )
    return render(request, "main/grid.html", dict(script=script))


def res_stationary(request: HttpRequest) -> HttpResponse:
    script = server_document(
        bokeh_base_url + url_prefix + "/bokeh_res", relative_urls=relative_urls
    )
    return render(request, "main/res.html", dict(script=script))


def non_res_stationary(request: HttpRequest) -> HttpResponse:
    script = server_document(
        bokeh_base_url + url_prefix + "/bokeh_non_res", relative_urls=relative_urls
    )
    return render(request, "main/non_res.html", dict(script=script))


def on_road_motor_veh(request: HttpRequest) -> HttpResponse:
    script = server_document(
        bokeh_base_url + url_prefix + "/bokeh_on_road", relative_urls=relative_urls
    )
    return render(request, "main/on_road.html", dict(script=script))


def rail(request: HttpRequest) -> HttpResponse:
    script = server_document(
        bokeh_base_url + url_prefix + "/bokeh_rail", relative_urls=relative_urls
    )
    return render(request, "main/rail.html", dict(script=script))


def aviation(request: HttpRequest) -> HttpResponse:
    script = server_document(
        bokeh_base_url + url_prefix + "/bokeh_aviation", relative_urls=relative_urls
    )
    return render(request, "main/aviation.html", dict(script=script))


def mobile_other(request: HttpRequest) -> HttpResponse:
    script = server_document(
        bokeh_base_url + url_prefix + "/bokeh_other", relative_urls=relative_urls
    )
    return render(request, "main/other.html", dict(script=script))


def non_energy(request: HttpRequest) -> HttpResponse:
    script = server_document(
        bokeh_base_url + url_prefix + "/bokeh_non_energy", relative_urls=relative_urls
    )
    return render(request, "main/non_energy.html", dict(script=script))


def sequestration_storage(request: HttpRequest) -> HttpResponse:
    script = server_document(
        bokeh_base_url + url_prefix + "/bokeh_seq", relative_urls=relative_urls
    )
    return render(request, "main/seq.html", dict(script=script))
