import os
import torch
import pymeshlab
import kaolin as kal
from .utils import device
from kaolin.io.obj import (import_mesh)
from torch.nn.functional import (normalize)

class Mesh():
    """
    AF(path, color) = a mesh representation of a 3d mesh object stored in path, initially set to color

    Representation Invariant:
        - true

    Representation Exporsure:
        - all fields are public for access
    """
    def __init__(self, path, color = torch.tensor([0.0, 0.0, 1.0]), mesh_type = "obj"):
        self.path = path
        self.mesh_set = pymeshlab.MeshSet()
        if mesh_type is None: self.mesh_set.add_mesh(path)
        elif mesh_type == "obj": self.mesh_set.load_new_mesh(path)
        self.obj = self.mesh_set.current_mesh()

        self.faces = torch.from_numpy(self.obj.face_matrix()).type(torch.int64).to(device)
        self.vertices = torch.from_numpy(self.obj.vertex_matrix()).float().to(device)
        self.face_normals = normalize(torch.from_numpy(self.obj.face_normal_matrix()).to(device).float())
        self.vertex_normals = normalize(torch.from_numpy(self.obj.vertex_normal_matrix()).to(device).float())
        self.base_color = torch.full(size=(self.faces.shape[0], 3, 3), fill_value=0.5, device=device)
        
        self.color = None
        self.face_uvs = None
        self.texture_map = None
        self.face_attributes = None

        self.set_texture_map_from_color(color)
        self.set_face_attributes_from_color(None)
    
    ### Helper Methods ###
    def set_texture_map_from_color(self, color):
        """
        Generates a texture map given a specific color of size (batch_size, colors = 3, h = 224, w = 224) 

        Inputs
            :color: <tensor> of color to generate texture map, has size (3 for rgb)
        """
        h, w = 224, 224
        texture_map = torch.zeros(1, h, w, 3).to(device)
        texture_map[:, :, :] = color
        self.texture_map = texture_map.permute(0, 3, 1, 2)

    def set_face_attributes_from_color(self, color):
        """
        Generatesface features given a specific color of size (batch_size, n_faces, face_vertices = 3, colors = 3)

        Inputs
            :color: <tensor> of color to generate face features, has size (3 for rgb)
        """
        if color is None: self.face_attributes = self.base_color
        else: 
            # print(f">> {self.base_color.shape} {kal.ops.mesh.index_vertices_by_faces(color.unsqueeze(0), self.faces).shape}")
            self.face_attributes = self.base_color + kal.ops.mesh.index_vertices_by_faces(color.unsqueeze(0), self.faces)
        self.color = color
        
    def export(self, path, color = False):
        """
        Exports the mesh to a file with a given color

        Inputs
            :path: <str> path to the file to export the mesh to
            :color: <boolean> indicating whether to save mesh color or not 
        """
        color = self.color if color else None 
        if isinstance(self.path, str):name, ext = os.path.splitext(os.path.basename(self.path))
        else: name, ext = "mesh", "obj"
        
        with open(path, "w+") as mesh_file:
            for i, vertex in enumerate(self.vertices):
                x, y, z = vertex
                mesh_file.write(f"v {x} {y} {z}")
                if color is not None: 
                    r, g, b = color[i]
                    mesh_file.write(f" {r} {g} {b}")
                mesh_file.write("\n")

                if self.vertex_normals is not None:
                    x, y, x = self.vertex_normals[i]
                    mesh_file.write(f"vn {x} {y} {z}\n")
            mesh_file.write("########## faces ##########\n")
            for face in self.faces:
                v1, v2, v3 = face
                mesh_file.write(f"f {v1 + 1} {v2 + 1} {v3 + 1}/\n")
                
            mesh_file.write(f"########## {name} ##########\n")
            mesh_file.write(f"##### faces: {len(self.faces)}\n")
            mesh_file.write(f"##### vertices: {len(self.vertices)}\n")
            mesh_file.write(f"##### vertex normals: {len(self.vertex_normals)}\n\n")
            mesh_file.close()
