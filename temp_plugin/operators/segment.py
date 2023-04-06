from pickle import TRUE
import bpy
import json
import bmesh
import requests 
import traceback

### Constants ###

class Seg_OT_Op(bpy.types.Operator):
    """ Segment a mesh """

    bl_idname = "mesh.seg"
    bl_label = "Process Mesh"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """Executes the segmentation"""
        return {'FINISHED'}
