"""
save model views
"""
import kaolin as kal
import json
from rest_framework import status
from utils.view_helpers import _is_subset
from rest_framework.response import Response
from rest_framework.decorators import api_view
import torch

import sys



@api_view(['POST'])
def save_model(request, *args, **kwargs):
    """
    Saves model as .obj in backend

    Inputs
        :request: <Response.HTTP> a requesting including the mesh specifying the vertices and the faces clusters to seperate mesh into, if None then number  | wbnnnis determined by finding the largest set of eigenvalues 
                         which are within ε away from each other, (default is None)
    
    Outputs
        :returns: <np.ndarray> Materials corresponding to the stylized mesh
    """
    try:
        request = json.loads(request.data)
        print(request)

        faces = request["faces"]
        vertices = request["vertices"]
        
        # Create a model with kaolin
        mesh = kal.rep.SurfaceMesh(vertices=torch.FloatTensor(vertices),
                           faces=torch.FloatTensor(faces),
                           allow_auto_compute=False)
        export(mesh, '/home/ubuntu/MechStyle-code/Models/Blender_Output/test/out.obj')
        # Proceed with your processing using the prompt
        # Return a successful response (adjust according to your function's actual response)
        return Response({"message": "Model saved successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        # Log the error or send it back in the response
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# Export from XMesh mesh
def export(mesh, file, color=None):
    with open(file, "w+") as f:
        for vi, v in enumerate(mesh.vertices):
            if color is None:
                f.write("v %f %f %f\n" % (v[0], v[1], v[2]))
            else:
                f.write("v %f %f %f %f %f %f\n" % (v[0], v[1], v[2], color[vi][0], color[vi][1], color[vi][2]))
            if mesh.vertex_normals is not None:
                f.write("vn %f %f %f\n" % (mesh.vertex_normals[vi, 0], mesh.vertex_normals[vi, 1], mesh.vertex_normals[vi, 2]))
        for face in mesh.faces:
            f.write("f %d %d %d\n" % (face[0] + 1, face[1] + 1, face[2] + 1))