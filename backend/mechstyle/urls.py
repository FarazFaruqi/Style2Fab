"""
stylize url patterns
"""
from . import views
from django.urls import path

urlpatterns = [
    path("", views.mechstyle, name = "mechstyle"),
]