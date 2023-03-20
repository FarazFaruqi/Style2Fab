"""
edit views
"""
import os
import sys
import json
import pymeshlab
import traceback 
import numpy as np
import pandas as pd
import scipy.sparse.linalg
from rest_framework import status
from django.shortcuts import render
from scipy.cluster.vq import kmeans2
from rest_framework.response import Response
from rest_framework.decorators import api_view
from utils.view_helpers import _is_subset, report
from segment.segment_utils.view_helpers import _remesh
from segment.segment_utils.reconstruct import reconstruct_mesh

#### Global Constant ####
component = "component"
model_dir = "/home/ubuntu/fa3ds/backend/segment/segment_utils/models"

@api_view(['POST'])
def fetch(request, *args, **kwargs):
    """
    Fetches requested mesh

    Inputs
        :request: <Response.HTTP> a requesting including the mesh specifying the vertices and the faces clusters to seperate mesh into, if None then number  | wbnnnis determined by finding the largest set of eigenvalues 
                         which are within ε away from each other, (default is None)
    
    Outputs
        :returns: modified mesh
    """
    data = {}
    request = json.loads(request.data)
    fetch_fields = ["i", "mesh_dir"]
    fetch_status = _is_subset(fetch_fields, request.keys())
    
    if fetch_status == status.HTTP_200_OK:
        # Step 0 (Initialization of variables)
        i = int(request['i'])
        mesh_dir = request['mesh_dir']
        print(f"Fetching mesh {i} from {mesh_dir} ...")

        mesh_path = None
        mesh, faces, vertices, face_segments = None, None, None, None
        labels = [
            "function", "function", "form", "function", "function", "form", "function", "form", "form", "function", "form", "function", 
            "function", "function", "form", "function", "function", "form", "function", "form", "form", "function", "form", "function",
            "form"
        ]
        
        try:
            num_meshes = 0
            mesh_found = False
            for file in os.listdir(mesh_dir): 
                mesh_path = f"{mesh_dir}/{file}"
                
                if os.path.isfile(mesh_path):
                    mesh_name, mesh_ext = os.path.splitext(mesh_path)
                    if mesh_ext != ".obj": continue
                    num_meshes += 1
                    if mesh_found: continue

                    if i == 0: 
                        ms = pymeshlab.MeshSet()
                        ms.load_new_mesh(mesh_path)
                        mesh = ms.current_mesh()
                        print(f"Found mesh at {mesh_path}!")
                        mesh_found = True
                    i -= 1

                if os.path.isdir(mesh_path):
                    try:
                        # print(f"Searching {mesh_path} ...")
                        num_meshes += 1
                        if mesh_found: continue
                        if i == 0: 
                            mesh, face_segments = reconstruct_mesh(mesh_path)
                            print(f"Found segmented mesh at {mesh_path}!")
                            labels_path = f"{mesh_path}/labels_{len(set(face_segments))}.csv"
                            if os.path.isfile(labels_path): 
                                labels_df = pd.read_csv(labels_path)
                                labels = list(labels_df['label'])

                            mesh_found = True
                    except Exception as error:                 
                        print(report(traceback.format_exc()))
                    i -= 1
        except Exception as error: print(report(traceback.format_exc()))

        if mesh is not None:
            faces = list(mesh.face_matrix())
            vertices = list(mesh.vertex_matrix())
        if face_segments is not None: 
            face_segments = list(face_segments)

        data['faces'] = faces
        data['vertices'] = vertices
        data['face_segments'] = face_segments
        data['meshId'] = mesh_path
        data['numMeshes'] = num_meshes
        data['failed'] = True if mesh is None else False
        print(f"[numMeshes] >> {data['numMeshes']}")
        print(f"[labels] >> {len(labels)} {labels}")
        data['labels'] = labels
        
    return Response(data = data, status = fetch_status)
