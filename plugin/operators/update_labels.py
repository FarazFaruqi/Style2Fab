import bpy
import json
import bmesh
import requests 

### Constants ###
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class UpdateLabels_OT_Op(bpy.types.Operator):
    """ Moves to next mesh """

    bl_idname = "mesh.update_labels"
    bl_label = "Update Labels"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """ Executes the fetching of the next mesh """
        return 