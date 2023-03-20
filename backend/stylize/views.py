"""
stylize views
"""
import json
import clip
import pymeshlab
import numpy as np
from rest_framework import status
from django.shortcuts import render
from utils.view_helpers import _is_subset
from rest_framework.response import Response
from .x2mesh.args import args as x2mesh_args
from rest_framework.decorators import api_view
from .x2mesh.implementation.main import x2mesh
from .x2mesh.implementation.utils import device
from .stylize_utils.view_helpers import _remesh

### Global Constants ###
print("Loading CLIP ...")
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
        prompt = request['prompt']
        remesh = request['remesh']
        selection = request['selection']
        faces = np.array(request['faces'])
        vertices = np.array(request['vertices'])
        n_iter = 200 

        mesh = pymeshlab.Mesh(vertices, faces)
        if remesh: mesh = _remesh(mesh)

        x2mesh_args['n_iter'] = n_iter
        x2mesh_args['obj_path'] = mesh
        x2mesh_args['prompt'] = prompt
        x2mesh_args['mesh_type'] = None
        x2mesh_args['verticies_in_file'] = False
        x2mesh_args['selected_vertices'] = selection

        mesh = x2mesh(x2mesh_args, clip_model, preprocess)
        
        materials = np.zeros((mesh.faces.shape[0], 4))
        for i, face in enumerate(mesh.faces):
            for v in face:
                for j, channel in enumerate(mesh.color[v]):
                    materials[i][j] += channel / 3
            materials[i, 3] = 1
        
        data['faces'] = mesh.faces.tolist()
        data['materials'] = materials.tolist()
        data['vertices'] = mesh.vertices.tolist()

    return Response(data = data, status = stylize_status)
