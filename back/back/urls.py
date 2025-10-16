from django.contrib import admin
from django.urls import path, include
from django.urls import path
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', lambda r: render(r, 'index.html')),
]

