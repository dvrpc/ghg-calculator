from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bokeh.embed import server_document


def index(request):
    return render(request, "main/intro.html")


def pop(request: HttpRequest) -> HttpResponse:
    script = server_document(
        "http://localhost:8013/app/ghg/bokeh-pop"
    )  # TODO: this works, but want to get rid of the domain
    # script = server_document(request.path + "bokeh-pop")
    return render(request, "main/pop.html", dict(script=script))


def res_stationary(request: HttpRequest) -> HttpResponse:
    script = server_document("http://localhost:8013/app/ghg/bokeh-res")
    return render(request, "main/res.html", dict(script=script))


def non_res_stationary(request: HttpRequest) -> HttpResponse:
    script = server_document("http://localhost:8013/app/ghg/bokeh-non-res")
    return render(request, "main/non_res.html", dict(script=script))


def on_road_motor_veh(request: HttpRequest) -> HttpResponse:
    script = server_document("http://localhost:8013/app/ghg/bokeh-on-road")
    return render(request, "main/on_road.html", dict(script=script))


def rail(request: HttpRequest) -> HttpResponse:
    script = server_document("http://localhost:8013/app/ghg/bokeh-rail")
    return render(request, "main/rail.html", dict(script=script))


def aviation(request: HttpRequest) -> HttpResponse:
    script = server_document("http://localhost:8013/app/ghg/bokeh-aviation")
    return render(request, "main/aviation.html", dict(script=script))


def mobile_other(request: HttpRequest) -> HttpResponse:
    script = server_document("http://localhost:8013/app/ghg/bokeh-other")
    return render(request, "main/other.html", dict(script=script))


def non_energy(request: HttpRequest) -> HttpResponse:
    script = server_document("http://localhost:8013/app/ghg/bokeh-non-energy")
    return render(request, "main/non_energy.html", dict(script=script))


def sequestration_storage(request: HttpRequest) -> HttpResponse:
    script = server_document("http://localhost:8013/app/ghg/bokeh-seq")
    return render(request, "main/seq.html", dict(script=script))


def electricity_grid(request: HttpRequest) -> HttpResponse:
    script = server_document("http://localhost:8013/app/ghg/bokeh-grid")
    return render(request, "main/grid.html", dict(script=script))
