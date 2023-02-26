import bpy
import json
import bmesh
import requests 
from .utils import get_segment_vertices, select_vertices

### Constants ###
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class NextSeg_OT_Op(bpy.types.Operator):
    """ Moves to next segment """

    bl_idname = "mesh.next_segment"
    bl_label = "next"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        objs = context.selected_objects
        if len(objs) == 1: return True
        print("Failed to get model because no object is selected")
        return False

    def execute(self, context):
        """Executes the segmentation"""
        selected_vertices = [] 
        # deselect everything
        select_vertices(context, selected_vertices)

        selected_vertices += get_segment_vertices(self, context, 1)
        
        select_vertices(context, selected_vertices)

        return {'FINISHED'}