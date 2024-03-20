"""
mechstyle views
"""
import json
from rest_framework import status
from utils.view_helpers import _is_subset
from rest_framework.response import Response
from rest_framework.decorators import api_view
import torch

import sys

# Add the directory containing the correct modules to the start of sys.path
sys.path.append('/home/ubuntu/MechStyle-code/Simulation_Code/XMesh')
# Now you can import the function from the module

#from stylize import Stylize
#from mesh import Mesh
#from render import Renderer
#from Normalization import MeshNormalizer
from run_mechStyle_geometric import run_stylize_and_mechstyle


@api_view(['POST'])
def mechstyle(request, *args, **kwargs):
    """
    Stylizes provided mesh with simulation

    Inputs
        :request: <Response.HTTP> a requesting including the mesh specifying the vertices and the faces clusters to seperate mesh into, if None then number  | wbnnnis determined by finding the largest set of eigenvalues 
                         which are within ε away from each other, (default is None)
    
    Outputs
        :returns: <np.ndarray> Materials corresponding to the stylized mesh
    """
    data = {}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    try:
        prompt = request.data.get("prompt", "")
        
        print(prompt)
        # Proceed with your processing using the prompt
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        run_stylize_and_mechstyle("/home/ubuntu/MechStyle-code/Models/Thingiverse_Models/Processed/bag_clip.obj", 
                                  "/home/ubuntu/MechStyle-code/Models/Blender_Output/bag_clip",
                                  "bag_clip", 
                                  prompt, 
                                  200, 
                                  mechStyle_bool=True, 
                                  device="cuda")
        # Return a successful response (adjust according to your function's actual response)
        return Response({"message": "Stylization completed successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        # Log the error or send it back in the response
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)