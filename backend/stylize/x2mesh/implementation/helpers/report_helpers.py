import os
import torch
import torchvision
import numpy as np
from ..render import Renderer
from ..utils import device
from kaolin.render.camera import (
   generate_perspective_projection
)

def _export_final(final_dir, mesh, losses, i):
    """
    Exports final obj after ith stylization iteration

    Inputs
        :final_dir: <str> path of directory to store final stylized mesh in
        :mesh: <Mesh> obj to store
        :losses: <tensor> of losses to store
        :i: <int> number of current stylization iteration
    """
    with torch.no_grad():
        mesh_name, ext = os.path.splitext(os.path.basename(mesh.path))
        mesh.export(os.path.join(final_dir, f"{mesh_name}_{i}_iters.obj"), True)

        torch.save(torch.tensor(losses), os.path.join(final_dir, "losses.pt"))

def _export_iters(iters_dir, mesh, n_views, i):
    """
    Inputs
        :iters_dir: <str> path of directory to store screenshots of the final stylized mesh in
        :mesh: <Mesh> obj to store screenshots of
        :n_views: <int> number of screenshots to store
        :i: <int> number of current stylization iteration
    """
    renderer = Renderer(mesh, camera=generate_perspective_projection(np.pi / 4, 1280 / 720).to(device), h=720, w=1280)
    rendered_images, _, _ = renderer(1, camera_distance=2.5)
    image_path = os.path.join(iters_dir, f"{i}_iters.jpg")
    torchvision.utils.save_image(rendered_images, image_path)