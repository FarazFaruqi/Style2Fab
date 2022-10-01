"""
segment url patterns
"""
from . import views
from django.urls import path

urlpatterns = [
    path("", views.segment, name = "segment"),
]