"""
assemble url patterns
"""
from . import views
from django.urls import path

urlpatterns = [
    path("", views.assemble, name = "assemble"),
]