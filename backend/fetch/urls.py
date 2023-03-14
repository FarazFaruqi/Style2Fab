"""
edit url patterns
"""
from . import views
from django.urls import path

urlpatterns = [
    path("", views.fetch, name = "fetch"),
]