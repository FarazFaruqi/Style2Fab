import bpy
import json
import bmesh
import requests 
from .utils import remove_mesh, add_mesh

### Constants ###
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class Delete_OT_Op(bpy.types.Operator):
    """ Delete a mesh """
    bl_idname = "object.delete"
    bl_label = "Object Delete Operator"
    
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
            try:
                for obj in bpy.context.selected_objects:

                    mesh_name = obj.name
                    for i in range(len(context.scene.models)): 
                        stored_model = context.scene.models[i]
                        if stored_model.name == mesh_name.lower(): 
                            context.scene.models.remove(i)
                            break

                    # Remove old mesh   
                    bpy.data.objects.remove(obj)
                self.report({'INFO'}, f"Removed mesh successfully!")

            except Exception as error: self.report({'INFO'}, f"Error occured while editing mesh\n{report(error)}")
            
            return {'FINISHED'}