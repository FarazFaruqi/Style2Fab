"""
segment views
"""
import os
import sys
import json
import pymeshlab
import numpy as np
import scipy.sparse.linalg
from rest_framework import status
from django.shortcuts import render
from scipy.cluster.vq import kmeans2
from utils.view_helpers import _is_subset
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .segment_utils.view_helpers import segment_mesh, _remesh, extract_segments
sys.setrecursionlimit(10000)

@api_view(['POST'])
def segment(request, *args, **kwargs):
    """
    Segments provided mesh

    Inputs
        :request: <Response.HTTP> a requesting including the mesh specifying the vertices and the faces clusters to seperate mesh into, if None then number  | wbnnnis determined by finding the largest set of eigenvalues 
                         which are within ε away from each other, (default is None)
    
    Outputs
        :returns: <np.ndarray> Labels of size m x 1; m = len(mesh.vertex_matrix) where Labels[i] = label of vertex i ∈ [1, k]
    """
    data = {}
    request = json.loads(request.data)
    segment_fields = ["vertices", "faces", "k", "collapsed"]
    segment_status   = _is_subset(segment_fields, request.keys())
    
    if segment_status == status.HTTP_200_OK:
        # Step 0 (Initialization of variables)
        k = request['k']
        remesh = request['remesh']
        collapsed = request['collapsed']
        faces = np.array(request['faces'])
        vertices = np.array(request['vertices'])
        
        mesh = pymeshlab.Mesh(vertices, faces)
        if remesh: mesh = _remesh(mesh)
        
        labels = segment_mesh(mesh, [k], collapsed = collapsed)
        extract_segments(vertices, faces, labels[0])

        data['face_segments'] = labels[0]
        data['faces'] = list(mesh.face_matrix())
        data['vertices'] = list(mesh.vertex_matrix())
        data['labels'] = [
            "function", "function", "form", "function", "function", "form", "function", "form", "form", "function", "form", "function", 
            "function", "function", "form", "function", "function", "form", "function", "form", "form", "function", "form", "function",
            "form"
        ]
        
    return Response(data = data, status = segment_status)
