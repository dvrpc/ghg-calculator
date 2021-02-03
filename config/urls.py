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
    path("population-and-development-patterns/", views.pop_dev_patterns),
    path("residential-stationary-energy/", views.res_stationary),
    path("non-residential-stationary-energy/", views.non_res_stationary),
    path("on-road-motor-vehicles/", views.on_road_motor_veh),
    path("rail/", views.rail),
    path("aviation/", views.aviation),
    path("other-mobile-energy/", views.mobile_other),
    path("non-energy/", views.non_energy),
    path("carbon-sequestration-and-storage/", views.sequestration_storage),
    path("electricity-grid/", views.electricity_grid),
]

bokeh_apps = [
    autoload("population-and-development-patterns", views.pop_dev_patterns_handler),
    autoload("residential-stationary-energy", views.res_stationary_handler),
    autoload("non-residential-stationary-energy", views.non_res_stationary_handler),
    autoload("on-road-motor-vehicles", views.on_road_motor_veh_handler),
    autoload("rail", views.rail_handler),
    autoload("aviation", views.aviation_handler),
    autoload("other-mobile-energy", views.mobile_other_handler),
    autoload("non-energy", views.non_energy_handler),
    autoload("carbon-sequestration-and-storage", views.sequestration_storage_handler),
    autoload("electricity-grid", views.electricity_grid_handler),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
