"""
edit views
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
from segment.segment_utils.edge import edge_collapse
from segment.segment_utils.mesh_graph import MeshGraph
from segment.segment_utils.view_helpers import _remesh
sys.setrecursionlimit(10000)

@api_view(['POST'])
def edit(request, *args, **kwargs):
    """
    Edits provided mesh

    Inputs
        :request: <Response.HTTP> a requesting including the mesh specifying the vertices and the faces clusters to seperate mesh into, if None then number  | wbnnnis determined by finding the largest set of eigenvalues 
                         which are within ε away from each other, (default is None)
    
    Outputs
        :returns: modified mesh
    """
    data = {}
    request = json.loads(request.data)
    edit_fields = ["vertices", "faces", "mode"]
    edit_status = _is_subset(edit_fields, request.keys())
    
    if edit_status == status.HTTP_200_OK:
        # Step 0 (Initialization of variables)
        mode = request['mode']
        faces = np.array(request['faces'])
        vertices = np.array(request['vertices'])

        print(f"Applying {mode} on mesh with {faces.shape[0]} faces and {vertices.shape[0]} verts ...")

        mesh = pymeshlab.Mesh(vertices, faces)
        vertices, faces = [], []
        if mode == "remesh": 
            mesh = _remesh(mesh)
            faces = list(mesh.face_matrix())
            vertices = list(mesh.vertex_matrix())
        if mode == "face collapse": 
            mesh_graph = MeshGraph(mesh)
            vertices, faces = mesh_graph.get_collapsed()
        elif mode == "edge collapse":
            mesh = edge_collapse(mesh, f=5000)
            faces = list(mesh.face_matrix())
            vertices = list(mesh.vertex_matrix())
                
        data['faces'] = faces
        data['vertices'] = vertices
        
    return Response(data = data, status = edit_status)
