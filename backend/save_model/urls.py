"""
stylize url patterns
"""
from . import views
from django.urls import path

urlpatterns = [
    path("", views.save_model, name = "save_model"),
]