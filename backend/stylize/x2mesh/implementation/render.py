import torch
import numpy as np
import kaolin as kal
from .utils import device
from kaolin.render.camera import (
   generate_transformation_matrix,
   generate_perspective_projection
)
from kaolin.render.mesh import (
    prepare_vertices,
    dibr_rasterization,
    spherical_harmonic_lighting
)

class Renderer():
    """
    AF(mesh, lights, camera, h, w) = setups a renderer camera with lights and caputres images of with given h, w for a given mesh

    Representation Invariant:

    Representation Exposure:
        
    """
    def __init__(self, mesh, lights = None, camera = None, h = 224, w = 224):
        self.mesh = mesh
        self.camera = camera
        if self.camera is None: 
            self.camera = generate_perspective_projection(np.pi / 3).to(device)
        
        self.lights = lights
        if self.lights is None: self.lights = torch.tensor([1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]).to(device)

        self.h = h
        self.w = w

    def __call__(self, n_views, elev = None, azim = None, camera_distance = 3):
        """
        Renders some front views of the mesh by first generating the transform matrix (i.e P_cam = P_world x M)
        
        Inputs
            :n_views: <int> number of views to render
            :std: <float> standard deviation
            :elev: <float> elevation angle, the angle between the vector from  the object to the camera and the horizontal plane (xy)
            :azim: <float> azimuth angle, the angle between the vector from the object to the camera projected onto a horizontal plane (y = 0) 
                           and a reference vector at (0 0 1) on the horizontal plane in [0, 360]
            :camera_distance: <int> distance of camera away from the mesh
        """
        n_faces = self.mesh.faces.shape[0]
        
        if elev is None:
            # elev = torch.linspace(0, np.pi / 2, n_views + 1)[:-1]
            elev = torch.cat((torch.tensor([0]), torch.randn(n_views - 1) * np.pi / 4))

        if azim is None:
            # azim = torch.linspace(0, np.pi, n_views + 1)[:-1]
            azim = torch.cat((torch.tensor([0]), torch.randn(n_views - 1) * np.pi / 2))

        camera_direction = torch.zeros((n_views, 3))
        for i in range(n_views): camera_direction[i, :] = torch.tensor([0.0, 1.0, 0.0])
        camera_position = -_spherical_to_cartesian(camera_distance, elev, azim)
        
        camera_transform = generate_transformation_matrix(camera_position, -camera_position, camera_direction).to(device)
        
        vertices_camera, vertices_world, face_normals = prepare_vertices(self.mesh.vertices, self.mesh.faces, self.camera, camera_transform=camera_transform)
        
        face_attributes = [self.mesh.face_attributes.repeat(n_views, 1, 1, 1), torch.ones((n_views, n_faces, 3, 1)).to(device)]
        
        image_features, soft_masks, face_index = dibr_rasterization(self.h, self.w, vertices_camera[:, :, :, -1], vertices_world, face_attributes, face_normals[:, :, -1])
        
        image_features, masks = image_features
        images = torch.clamp(image_features, 0, 1)
        image_normals = face_normals[:, face_index][0]
        lighting = spherical_harmonic_lighting(image_normals, self.lights.repeat(n_views, 1)).unsqueeze(0)
        
        # the lighting is of shape (b, h, w) and images are (b, h, w, c)
        # we convert lighting (b, h, w) -> (b, c, h, w) -> (b, h, w, c) where c = 3
        images = torch.clamp(images * lighting.repeat(3, 1, 1, 1).permute(1, 2, 3, 0).to(device), 0, 1)
        
        # changing backgorund to be white
        masks = masks.squeeze(-1)
        background_mask = torch.zeros(images.shape).to(device)
        assert torch.all(images[torch.where(masks == 0)] == torch.zeros(3).to(device))
        background_mask[torch.where(masks == 0)] = torch.tensor([1, 1, 1]).to(device).float()
        images = torch.clamp(images + background_mask, 0, 1)
        
        return images.permute(0, 3, 1, 2), elev, azim
 
def _spherical_to_cartesian(r, elev, azim):
    """Converts spherical elevation and azium angle coordinates to cartesian coordinates"""
    cartesian_coords = torch.zeros((3, len(elev)))
    cartesian_coords[0, :] = r * torch.cos(elev) * torch.cos(azim)  # x
    cartesian_coords[1, :] = r * torch.sin(elev)                    # y
    cartesian_coords[2, :] = r * torch.cos(elev) * torch.sin(azim)  # z

    cartesian_coords = cartesian_coords.permute(1, 0)
    return cartesian_coords
    