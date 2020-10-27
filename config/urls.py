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

from bokeh.server.django import autoload, directory, document, static_extensions

from main import views

bokeh_app_config = apps.get_app_config("bokeh.server.django")

urlpatterns = [
    path("admin", admin.site.urls),
    path("", views.index, name="index"),
    path("population/", views.population, name="population"),
    path("stationary_energy/", views.stationary_energy),
    path("mobile_energy/", views.mobile_energy),
    path("grid_mix/", views.grid_mix),
]

bokeh_apps = [
    autoload("population", views.population_handler),
    autoload("stationary_energy", views.stationary_energy_handler),
    autoload("mobile_energy", views.mobile_energy_handler),
    autoload("grid_mix", views.grid_mix_handler),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
