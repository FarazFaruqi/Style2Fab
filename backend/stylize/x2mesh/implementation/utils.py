import os
import re
import torch
import shutil
import argparse
import pymeshlab 
import numpy as np

### Global Constans ###
yes = {"yes", "y", "yeah", "yea"}
if torch.cuda.is_available():
    device = torch.device("cuda:0")
    torch.cuda.set_device(device)
else: device = torch.device("cpu")

### Functions ###
def read_mesh(mesh_path):
    """
    Reads a 3d mesh and previews the result

    Inputs
        :mesh_path: <str> path to the mesh obj represnetation
    """
    with open(mesh_path, 'r', encoding='utf-8') as mesh_file:
        lines = mesh_file.read().splitlines()
        for i in range(len(lines)):
            if "f " in lines[i]: print(f"{i} {lines[i]}")
    
def check_mesh(mesh_path):
    """
    Checks whether the number of verticies equals the number of vertex normals in a mesh and produces a warning or fails if they are not
    Changes the text2mesh mesh.py to reflect the discripency within the mesh file

    Inputs
        :mesh_path: <str> path to the mesh obj represnetation
        :text2mesh_path: <str> path to the text2mesh cloned repo

    Throws
        <ValueError> if the number of verticies > number of vertex normals
    """
    with open(mesh_path, 'r', encoding='utf-8') as mesh_file:
        mesh_file_content = mesh_file.read()
        num_vertices = len(re.findall("v .*", mesh_file_content))
        num_normals = len(re.findall("vn .*", mesh_file_content))

        if num_normals == 0: 
            raise ValueError(f"\033[91mFail: Could not determine number of vertex normals in {mesh_path}\033[0m")

        mesh_file.close()
        
        if num_vertices != num_normals: 
            print(f"\033[93mCaution[{mesh_path} Deprecated]: Number of verticies ({num_vertices}) != the number of normals ({num_normals})\033[0m")
            remesh = input("Do you want to remesh? (y, [n]): ")
            if remesh.lower() in yes:
                print(f"Remeshing ...")
                ms = pymeshlab.MeshSet()
                ms.load_new_mesh(mesh_path)
                ms.meshing_isotropic_explicit_remeshing()
                ms.save_current_mesh(f"{mesh_path}")
                return check_mesh(mesh_path)
            else:
                remove = input("Do you want to remove this model? (y, [n]): ")
                if remove in yes: os.remove(mesh_path)

        else: print(f"\033[92mSuccess[{mesh_path} is good!]: Number of verticies ({num_vertices}) == the number of normals ({num_normals})\033[0m")

class FourierFeatureTransform(torch.nn.Module):
    """
    An implementation of Gaussian Fourier feature mapping.
    "Fourier Features Let Networks Learn High Frequency Functions in Low Dimensional Domains":
       https://arxiv.org/abs/2006.10739
       https://people.eecs.berkeley.edu/~bmild/fourfeat/index.html
    Given an input of size [batches, num_input_channels, width, height],
     returns a tensor of size [batches, mapping_size*2, width, height].
    """

    def __init__(self, num_input_channels, mapping_size=256, scale=10, exclude=0):
        super().__init__()

        self._num_input_channels = num_input_channels
        self._mapping_size = mapping_size
        self.exclude = exclude
        B = torch.randn((num_input_channels, mapping_size)) * scale
        B_sort = sorted(B, key=lambda x: torch.norm(x, p=2))
        self._B = torch.stack(B_sort)  # for sape

    def forward(self, x):
        # assert x.dim() == 4, 'Expected 4D input (got {}D input)'.format(x.dim())

        batches, channels = x.shape

        assert channels == self._num_input_channels, \
            "Expected input to have {} channels (got {} channels)".format(self._num_input_channels, channels)

        # Make shape compatible for matmul with _B.
        # From [B, C, W, H] to [(B*W*H), C].
        # x = x.permute(0, 2, 3, 1).reshape(batches * width * height, channels)

        res = x @ self._B.to(x.device)

        # From [(B*W*H), C] to [B, W, H, C]
        # x = x.view(batches, width, height, self._mapping_size)
        # From [B, W, H, C] to [B, C, W, H]
        # x = x.permute(0, 3, 1, 2)

        res = 2 * np.pi * res
        return torch.cat([x, torch.sin(res), torch.cos(res)], dim=1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--mesh_path', type=str, default='/content/implementation/inputs/cat.obj')
    parser.add_argument('--text2mesh_path', type=str, default='/content/text2mesh')
    
    args = parser.parse_args()
    check_mesh(args.mesh_path, args.text2mesh_path)