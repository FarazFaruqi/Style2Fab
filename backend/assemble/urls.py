"""
assemble url patterns
"""
from . import views
from django.urls import path

urlpatterns = [
    path("assemble", views.assemble, name = "assemble"),
]