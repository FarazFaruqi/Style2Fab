"""
stylize views
"""
from rest_framework import status
from django.shortcuts import render
from utils.view_helpers import _is_subset
from rest_framework.response import Response
from rest_framework.decorators import api_view