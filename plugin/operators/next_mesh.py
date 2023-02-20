import bpy
import json
import bmesh
import requests 
from .utils import remove_mesh, add_mesh, fetch

### Constants ###
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class Next_OT_Op(bpy.types.Operator):
    """ Moves to next mesh """

    bl_idname = "mesh.next_mesh"
    bl_label = "next"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """ Executes the fetching of the next mesh """
        i = context.scene.i + 1
        return fetch(self, context, i)