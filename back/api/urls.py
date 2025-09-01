from django.urls import path
from . import views

urlpatterns = [
    path("calcular/", views.calcular, name="calcular"),
    path("", views.index, name="index"),
]
