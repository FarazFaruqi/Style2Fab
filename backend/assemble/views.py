"""
assemble views
"""
import os
import sys
import json
import traceback
import pymeshlab
import numpy as np
from rest_framework import status
from django.shortcuts import render
from utils.view_helpers import _is_subset, report
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .assemble_utils.similarity import similarity

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
        mesh_set = request['meshSet']
   
        similarities = {}
        print(f"Initiating similarity measuring ...")
        for mesh_id, i, faces, vertices in mesh_set:
            faces = np.array(faces)
            vertices = np.array(vertices)
            mesh = pymeshlab.Mesh(face_matrix=faces, vertex_matrix=vertices)
            for other_id, j, faces_other, vertices_other in mesh_set:
                faces = np.array(faces)
                vertices = np.array(vertices)
                mesh_other = pymeshlab.Mesh(face_matrix=faces_other, vertex_matrix=vertices_other)
                
                ms = pymeshlab.MeshSet()
                ms.add_mesh(mesh)
                ms.add_mesh(mesh_other)

                try:
                    print(f"Initiating similarity measuring ...")
                    # sim = similarity(ms, wait=None)
                    sim = 0
                    if (mesh_id, i) in similarities: similarities[(mesh_id, i)].append(((other_id, j), sim))
                    else: similarities[i] = [((other_id, j), sim)]

                    print(f"[sim] >> segment {i} ~ segment {j} = {float(sim):.3f}")
                except Exception as error: 
                    raise error
                    print(report(f"{traceback.format_exc()}\nAssembly failed :("))

                ms.clear()
        
            
            data['similarities'] = similarities

    return Response(data = data, status = assemble_status)
