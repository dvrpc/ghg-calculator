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
from django.urls import path

from main import views

urlpatterns = [
    path("", views.index, name="index"),
    path("population-and-development-patterns/", views.pop, name="pop"),
    path("residential-stationary-energy/", views.res_stationary, name="res"),
    path("non-residential-stationary-energy/", views.non_res_stationary, name="non_res"),
    path("on-road-motor-vehicles/", views.on_road_motor_veh, name="on_road"),
    path("rail/", views.rail, name="rail"),
    path("aviation/", views.aviation, name="aviation"),
    path("other-mobile-energy/", views.mobile_other, name="other"),
    path("non-energy/", views.non_energy, name="non_energy"),
    path("carbon-sequestration-and-storage/", views.sequestration_storage, name="seq"),
    path("electricity-grid/", views.electricity_grid, name="grid"),
]
