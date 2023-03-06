"""
assemble views
"""
import os
import sys
import json
import pymeshlab
from rest_framework import status
from django.shortcuts import render
from utils.view_helpers import _is_subset
from rest_framework.response import Response
from rest_framework.decorators import api_view

### Global Constants ###
default_models_dir = "/home/ubuntu/fa3ds/backend/results/segmented_models"

@api_view(['POST'])
def assemble(request, *args, **kwargs):
    """
    Assembles a given set of meshes by searching for similarities within components

    Inputs
        :request: <Response.HTTP> 
    
    Outputs
        :returns: modified mesh
    """
    data = {}
    request = json.loads(request.data)
    assemble_fields = ["meshSet"]
    assemble_status = _is_subset(assemble_fields, request.keys())
    
    if assemble_status == status.HTTP_200_OK:
        # Step 0 (Initialization of variables)
        mesh_set = request['meshSet']

    return Response(data = data, status = assemble_status)
