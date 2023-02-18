import bpy
import json
import bmesh
import requests 
from .utils import remove_mesh, add_mesh

### Constants ###
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class Edit_OT_Op(bpy.types.Operator):
    """ Edit a mesh """

    bl_idname = "mesh.edit_mesh"
    bl_label = "Edit mesh"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        obj = context.object
        if obj is not None: return True
        print("\033[32m[Error] >> Failed to get model because no object is selected\033[0m")
        
        return False

    def execute(self, context):
        """Executes the segmentation"""
        if bpy.ops.mesh.separate(type='LOOSE') != {'CANCELLED'}:
            self.report({'ERROR'}, "Separated not connected parts, choose one of them for segmentation!")
            return {'CANCELLED'}
        else:
            mode = context.scene.mode
            objs = [obj for obj in bpy.context.selected_objects]
            for obj in objs:
                vertices = []
                for vertex in obj.data.vertices: vertices.append(vertex.co[:])

                faces = []
                for face in obj.data.polygons: faces.append([i for i in face.vertices])

                url = "http://0.0.0.0:8000/edit/"

                data = json.dumps({'vertices': vertices, 'faces': faces, 'mode': mode})

                try:
                    response = requests.post(url = url, json = data).json()
                    
                    faces = response['faces']
                    vertices = response['vertices']
                    self.report({'INFO'}, f"Remeshed successfully!")
                    
                    mesh_name = obj.name
                    # Remove old mesh   
                    remove_mesh(self, mesh_name)

                    # Add new mesh
                    new_object = add_mesh(self, mesh_name, vertices, faces)

                except Exception as error: print(f"Error occured while editing mesh\n{report(error)}")
                
            return {'FINISHED'}