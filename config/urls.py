"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from bokeh.server.django import autoload

from main import views

bokeh_app_config = apps.get_app_config("bokeh.server.django")

urlpatterns = [
    # path("admin", admin.site.urls),
    path("", views.index, name="index"),
    path("population/", views.population),
    path("res_stationary/", views.res_stationary),
    path("ci_stationary/", views.ci_stationary),
    path("mobile_highway/", views.mobile_highway),
    path("mobile_transit/", views.mobile_transit),
    path("mobile_aviation/", views.mobile_aviation),
    path("mobile_other/", views.mobile_other),
    path("non_energy/", views.non_energy),
    path("grid_mix/", views.grid_mix),
]

bokeh_apps = [
    autoload("population", views.population_handler),
    autoload("res_stationary", views.res_stationary_handler),
    autoload("ci_stationary", views.ci_stationary_handler),
    autoload("mobile_highway", views.mobile_highway_handler),
    autoload("mobile_transit", views.mobile_transit_handler),
    autoload("mobile_aviation", views.mobile_aviation_handler),
    autoload("mobile_other", views.mobile_other_handler),
    autoload("non_energy", views.non_energy_handler),
    autoload("grid_mix", views.grid_mix_handler),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
