"""
stylize views
"""
import json
import clip
import pymeshlab
import numpy as np
from x2mesh.args import args
from rest_framework import status
from django.shortcuts import render
from utils.view_helpers import _is_subset
from rest_framework.response import Response
from x2mesh.implementation.main import x2mesh
from x2mesh.implementation.utils import device
from rest_framework.decorators import api_view

### Global Constants ###
clip_model, preprocess = clip.load('ViT-B/32', device, jit=False)

@api_view(['POST'])
def stylize(request, *args, **kwargs):
    """
    Stylizes provided mesh

    Inputs
        :request: <Response.HTTP> a requesting including the mesh specifying the vertices and the faces clusters to seperate mesh into, if None then number  | wbnnnis determined by finding the largest set of eigenvalues 
                         which are within ε away from each other, (default is None)
    
    Outputs
        :returns: <np.ndarray> Materials corresponding to the stylized mesh
    """
    data = {}
    request = json.loads(request.data)
    stylize_fields = ["vertices", "faces", "prompt", "selection"]
    stylize_status   = _is_subset(stylize_fields, request.keys())
    
    if stylize_status == status.HTTP_200_OK:
        faces = np.array(request['faces'])
        vertices = np.array(request['vertices'])

        args['obj_path'] = pymeshlab.Mesh(vertices, faces)
        mesh = x2mesh(args, clip_model, preprocess)
        
        materials = np.ones(mesh.faces.shape)
        
        data['faces'] = json.dumps(list(mesh.faces))
        data['materials'] = json.dumps(list(materials))
        data['vertices'] = json.dumps(list(mesh.vertices))

    return Response(data = data, status = stylize_status)
