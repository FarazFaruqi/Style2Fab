"""
classification views
"""
import os
import sys
import json
import pymeshlab
import numpy as np
import pandas as pd
import scipy.sparse.linalg
from rest_framework import status
from django.shortcuts import render
from utils.view_helpers import _is_subset
from rest_framework.response import Response
from rest_framework.decorators import api_view

### Global Constants ###
default_models_dir = "/home/ubuntu/fa3ds/backend/results/api_segmented_models"

@api_view(['POST'])
def annotate(request, *args, **kwargs):
    """
    Annotate provided mesh

    Inputs
        :request: <Response.HTTP> 
    
    Outputs
        :returns: modified mesh
    """
    data = {}
    request = json.loads(request.data)
    annotate_fields = ["meshId", "labels"]
    annotate_status = _is_subset(annotate_fields, request.keys())
    
    if annotate_status == status.HTTP_200_OK:
        # Step 0 (Initialization of variables)
        labels = request['labels']
        mesh_id = request['meshId']
        mesh_dir = request['meshDir'] if 'meshDir' in request else default_models_dir
        labels_path = f"{mesh_dir}/model_{mesh_id}/labels_{len(labels)}.csv"
        
        df = pd.DataFrame([[mesh_id, i ,labels[i]] for i in range(len(labels))], columns=["meshId", "segmentNo", "label"])
        df.to_csv(labels_path, encoding='utf-8', index=False)

    return Response(data = data, status = annotate_status)
