import os
import re
import pymeshlab
from view_helpers import batch_seg

#### Global Constants ####
accepted_formats = ['.stl']

class MeshEditor():
    """
    AF() = 

    """
    def __init__(self):
        return
    
    def to_obj(self, mesh_path, output_path = None):
        """
        Converts a mesh from any format to obj

        Inputs
            :mesh_path: <str> stl path of the mesh to convert to obj or path to a dir containing stl meshes
        
        Outputs
            :returns: <list> of converted meshes 
        """
        if os.path.isfile(mesh_path):  
            return [self.__file_to_obj(mesh_path, output_path)]
        meshes = []
        for _, dirs, files in os.walk(mesh_path):
            for dir in dirs: meshes.append(self.to_obj(f"{mesh_path}/{dir}", output_path))
            for file in files: meshes += self.to_obj(f"{mesh_path}/{file}", output_path)
        return meshes

    #### Helper Methods ####
    def __file_to_obj(self, mesh_path, output_path = None):
        mesh_name, mesh_ext = os.path.splitext(mesh_path)
        if mesh_ext == ".obj": return
        # print(f"Converting {mesh_ext} mesh -> obj ...")
        if mesh_ext not in accepted_formats: return
        if output_path is None: output_path = f"{mesh_name}.obj"

        # loading mesh
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(mesh_path)

        ms.save_current_mesh(output_path)
        # print("--- Done ---")

    def batch_seg(self, meshes, num_segments):
        """
        Batch segmentation of a list of meshes with corresponding num_segments

        Inputs
            :meshes: 
            :num_segments:
        """
        assert len(meshes) == len(num_segments)
        return batch_seg([(meshes[i], num_segments[i]) for i in range(len(meshes))])

if __name__ == "__main__":
    mesh_editor = MeshEditor()

    stl_paths = [
        '/home/ubuntu/fa3ds/backend/segment/segment_utils/models/base.stl', 
        '/home/ubuntu/fa3ds/backend/segment/segment_utils/models/knob.stl',
        '/home/ubuntu/fa3ds/backend/segment/segment_utils/models/pinch.stl'
    ]
    
    for model_path in stl_paths:
        mesh_editor.to_obj(model_path)
