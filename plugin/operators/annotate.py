import bpy
import json
import bmesh
import requests 
from .utils import get_segment_vertices, select_vertices, report

### Constants ###

class Annotate_OT_Op(bpy.types.Operator):
    """ Annotates a mesh by storing the labels """

    bl_idname = "mesh.annotate"
    bl_label = "annotate"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        objs = context.selected_objects
        if len(objs) == 1: return True
        print("Failed to get model because no object is selected")
        return False

    def execute(self, context):
        """Executes the segmentation"""
        

        return {'FINISHED'}