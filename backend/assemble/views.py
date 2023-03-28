"""
assemble views
"""
import os
import sys
import json
import random
import traceback
import pymeshlab
import numpy as np
import pandas as pd
from rest_framework import status
from django.shortcuts import render
from utils.view_helpers import _is_subset, report
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .assemble_utils.similarity import similarity

### Global Constants ###
all_similarity = "/home/ubuntu/fa3ds/user_study/models/similarity.csv"
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
                if mesh_id == other_id: 
                    if f"{mesh_id},{i}" in similarities: similarities[f"{mesh_id},{i}"].append(((other_id, j), 1.00))
                    else: similarities[f"{mesh_id},{i}"] = [((other_id, j), 1.00)]
                    continue
                faces_other = np.array(faces_other)
                vertices_other = np.array(vertices_other)
                mesh_other = pymeshlab.Mesh(face_matrix=faces_other, vertex_matrix=vertices_other)
                
                ms = pymeshlab.MeshSet()
                ms.add_mesh(mesh)
                ms.add_mesh(mesh_other)

                try:
                    print(f"Initiating similarity measuring ...")
                    sim = None
                    if os.path.isfile(all_similarity): 
                        sim_df = pd.read_csv(all_similarity)
                        sim = list(sim_df[(sim_df['meshId'] == mesh_id)     & 
                                            (sim_df['otherId'] == other_id) & 
                                            (((sim_df['i'] == i) & (sim_df['j'] == j)) |
                                            ((sim_df['j'] == i) & (sim_df['i'] == j)))
                                            ]['sim'])
                        if len(sim) > 0: sim = sim[-1]
                        else: sim = None
                    if sim is None: 
                        print(f"Could not find {mesh_id},{other_id},{i},{j}")
                        sim = similarity(ms, wait=None)[1]

                    if f"{mesh_id},{i}" in similarities: similarities[f"{mesh_id},{i}"].append(((other_id, j), sim))
                    else: similarities[f"{mesh_id},{i}"] = [((other_id, j), sim)]

                    print(f"[sim] >> segment {i} ~ segment {j} = {float(sim):.2f}")
                except Exception as error: 
                    print(report(f"{traceback.format_exc()}\nAssembly failed :("))

                ms.clear()
        
            
            data['similarities'] = similarities

    return Response(data = data, status = assemble_status)
