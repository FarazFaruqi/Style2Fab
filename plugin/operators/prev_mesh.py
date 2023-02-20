import bpy
import json
import bmesh
import requests 
from .utils import remove_mesh, add_mesh, fetch

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
        return fetch(self, context, i)