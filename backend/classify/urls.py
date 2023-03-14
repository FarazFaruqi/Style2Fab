"""
classification url patterns
"""
from . import views
from django.urls import path

urlpatterns = [
    path("annotate", views.annotate, name = "annotate"),
]