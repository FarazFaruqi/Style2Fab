"""
edit views
"""
import kaolin as kal
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
default_labels = [
    "function", "function", "form", "function", "function", "form", "function", "form", "form", "function", "form", "function", 
    "function", "function", "form", "function", "function", "form", "function", "form", "form", "function", "form", "function",
    "form"
]

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
        meshes, meshes_found, face_segments_list, labels, num_meshes = [], [], [], [default_labels], 0

        try:
            meshes, meshes_found, face_segments_list, labels, num_meshes = _find_mesh(mesh_dir, i)
        except Exception as error: print(report(f"failed on {mesh_dir}\n{traceback.format_exc()}"))
        
        # updated to use kaolin
        for mesh in meshes:
            #print(mesh)
            #mesh.compact()
            
            faces = [mesh.faces]
            vertices = [mesh.vertices]
                
        #faces = [list(mesh.face_matrix()) for mesh in meshes]
        #vertices = [list(mesh.vertex_matrix()) for mesh in meshes]
        # if face_segments is not None: 
        #     face_segments = list(face_segments)

        data['faces'] = faces
        data['labels'] = labels
        data['vertices'] = vertices
        data['meshIds'] = meshes_found
        data['numMeshes'] = num_meshes
        data['face_segments'] = face_segments_list
        data['failed'] = True if len(meshes) == 0 else False
        print(f"[numMeshes] >> {data['numMeshes']}")
        print(f"[labels] >> {len(labels)} {labels}")
        
    return Response(data = data, status = fetch_status)

### Helper Functions ###
def _find_mesh(mesh_dir, i):
    meshes = []
    num_meshes = 0
    labels_list = []
    meshes_found = []
    face_segments_list = []
    if os.path.isdir(mesh_dir):
        for file in os.listdir(mesh_dir): 
            mesh_path = f"{mesh_dir}/{file}"
            # print(f"Checking {mesh_path} ...")
    if os.path.isdir(mesh_dir):
        for file in os.listdir(mesh_dir): 
            mesh_path = f"{mesh_dir}/{file}"
            # print(f"Checking {mesh_path} ...")

            if os.path.isfile(mesh_path):
                mesh_name, mesh_ext = os.path.splitext(mesh_path)
                if mesh_ext != ".obj": continue
                num_meshes += 1
                # if meshes_found is not None: continue
            if os.path.isfile(mesh_path):
                mesh_name, mesh_ext = os.path.splitext(mesh_path)
                if mesh_ext != ".obj": continue
                num_meshes += 1
                # if meshes_found is not None: continue

                if i is None or i == 0: 
                    ms = pymeshlab.MeshSet()
                    ms.load_new_mesh(mesh_path)
                    mesh = ms.current_mesh()
                    print(f"Found mesh at {mesh_path}!")
                if i is None or i == 0: 
                    ms = pymeshlab.MeshSet()
                    ms.load_new_mesh(mesh_path)
                    mesh = ms.current_mesh()
                    print(f"Found mesh at {mesh_path}!")

                    meshes.append(mesh)
                    labels_list.append(default_labels)
                    meshes_found.append(mesh_path)
                    face_segments_list.append(None)
                if i is not None: 
                    i -= 1
                    meshes.append(mesh)
                    labels_list.append(default_labels)
                    meshes_found.append(mesh_path)
                    face_segments_list.append(None)
                if i is not None: i -= 1

            if os.path.isdir(mesh_path):
                if i is None or i == 0:
                    if len([1 for comp_path in os.listdir(mesh_path) if os.path.isfile(f"{mesh_path}/{comp_path}")]) != 0:
                        try:
                            print(f"Searching {mesh_path} for {i}th mesh ...")
                            num_meshes += 1
                            # if len(meshes_found) > 0: continue
                            mesh, face_segments = reconstruct_mesh(mesh_path)
                            print(f"Found segmented mesh at {mesh_path}!")
                            labels_path = f"{mesh_path}/labels_{len(set(face_segments))}.csv"
                            labels = default_labels
                            if os.path.isfile(labels_path): 
                                labels_df = pd.read_csv(labels_path)
                                labels = list(labels_df['label'])
                            
                            meshes.append(mesh)
                            labels_list.append(labels)
                            meshes_found.append(mesh_path)
                            face_segments_list.append(face_segments)
                        except Exception: print(report(f"failed on {mesh_path}\n{traceback.format_exc()}"))
                    else:
                        print(report(f"failed on {mesh_path}\n{traceback.format_exc()}"))
                        j = len([1 for comp_path in os.listdir(mesh_path) if os.path.isdir(f"{mesh_path}/{comp_path}")]) - 1
                        
                        print(f"Searching for {j} meshes inside {mesh_path}")
                        child_meshes, child_meshes_found, child_face_segments, child_labels, _ = _find_mesh(mesh_path, None)
            if os.path.isdir(mesh_path):
                if i is None or i == 0:
                    if len([1 for comp_path in os.listdir(mesh_path) if os.path.isfile(f"{mesh_path}/{comp_path}")]) != 0:
                        try:
                            print(f"Searching {mesh_path} for {i}th mesh ...")
                            num_meshes += 1
                            # if len(meshes_found) > 0: continue
                            mesh, face_segments = reconstruct_mesh(mesh_path)
                            print(f"Found segmented mesh at {mesh_path}!")
                            labels_path = f"{mesh_path}/labels_{len(set(face_segments))}.csv"
                            labels = default_labels
                            if os.path.isfile(labels_path): 
                                labels_df = pd.read_csv(labels_path)
                                labels = list(labels_df['label'])
                            
                            meshes.append(mesh)
                            labels_list.append(labels)
                            meshes_found.append(mesh_path)
                            face_segments_list.append(face_segments)
                        except Exception: print(report(f"failed on {mesh_path}\n{traceback.format_exc()}"))
                    else:
                        print(report(f"failed on {mesh_path}\n{traceback.format_exc()}"))
                        j = len([1 for comp_path in os.listdir(mesh_path) if os.path.isdir(f"{mesh_path}/{comp_path}")]) - 1
                        
                        print(f"Searching for {j} meshes inside {mesh_path}")
                        child_meshes, child_meshes_found, child_face_segments, child_labels, _ = _find_mesh(mesh_path, None)

                        meshes += child_meshes
                        labels_list += child_labels
                        meshes_found += child_meshes_found
                        face_segments_list += child_face_segments
                if i is not None: i -= 1
    elif os.path.isfile(mesh_dir) and os.path.splitext(mesh_dir)[1] == '.obj':
        print("this is called")
        # Handle the case where mesh_dir is a direct path to an .obj file
        
        #ms = pymeshlab.MeshSet()
        #ms.load_new_mesh(mesh_dir)
        #mesh = ms.current_mesh()
        #print(f"Found mesh at {mesh_dir}!")
        mesh = kal.io.obj.import_mesh(mesh_dir, with_normals=True)

        meshes.append(mesh)
        labels_list.append(default_labels)
        meshes_found.append(mesh_dir)
        face_segments_list.append(None)
        num_meshes = 1  
    else:
        print(f"Path provided is neither a directory nor an .obj file: {mesh_dir}")
    
    return meshes, meshes_found, face_segments_list, labels_list, num_meshes