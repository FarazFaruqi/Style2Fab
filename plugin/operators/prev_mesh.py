import bpy
import json
import bmesh
import requests 
from .utils import remove_mesh, add_mesh

### Constants ###
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class Prev_OT_Op(bpy.types.Operator):
    """ Moves to previous mesh """

    bl_idname = "mesh.prev_mesh"
    bl_label = "prev"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """Executes the segmentation"""
        i = context.scene.i - 1
        mesh_dir = context.scene.mesh_dir
        
        mesh_name = "Loaded"
        url = "http://0.0.0.0:8000/fetch/"

        self.report({'INFO'}, f"Loading Mesh {i} ...")
        data = json.dumps({'i': i, 'mesh_dir': mesh_dir})
        try:
            response = requests.post(url = url, json = data).json()
            
            faces = response['faces']
            vertices = response['vertices']
            self.report({'INFO'}, f"Loaded mesh successfully!")
            
            # Remove old mesh   
            remove_mesh(self, mesh_name)

            # Add new mesh
            new_object = add_mesh(self, mesh_name, vertices, faces)

            context.scene.i = i 
        except Exception as error: print(f"Error occured while editing mesh\n{report(error)}")
                
        return {'FINISHED'}