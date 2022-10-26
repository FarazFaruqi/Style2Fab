import torch

class MeshNormalizer:
    """
    """

    def __init__(self, mesh):
        self.mesh = mesh  # original copy of the mesh
        self.normalizer = Normalizer.get_bounding_sphere_normalizer(self.mesh.vertices)

    def __call__(self):
        """ """
        self.mesh.vertices = self.normalizer(self.mesh.vertices)
        return self.mesh

class Normalizer:
    """
    """

    @classmethod
    def get_bounding_box_normalizer(cls, x):
        """ """
        shift = torch.mean(x, dim = 0)
        scale = torch.max(torch.norm(x - shift, p = 1, dim = 1))
        return Normalizer(scale = scale, shift = shift)

    @classmethod
    def get_bounding_sphere_normalizer(cls, x):
        """ """
        shift = torch.mean(x, dim=0)
        scale = torch.max(torch.norm(x - shift, p = 2, dim = 1))
        return Normalizer(scale = scale, shift = shift)

    def __init__(self, scale, shift):
        self.scale = scale
        self.shift = shift

    def __call__(self, x):
        """ """
        return (x - self.shift) / self.scale

    def get_de_normalizer(self):
        """ """
        invscale = 1 / self.scale
        invshift = - self.shift / self.scale
        return Normalizer(scale = invscale, shift = invshift)