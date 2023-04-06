from pickle import TRUE
import bpy
import json
import bmesh
import requests 
import traceback

### Constants ###

class Sim_OT_Op(bpy.types.Operator):
    """ Segment a mesh """

    bl_idname = "mesh.sim"
    bl_label = "Similarity"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """Executes the segmentation"""
        return {'FINISHED'}
