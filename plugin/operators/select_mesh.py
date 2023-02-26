import bpy
import json
import bmesh
import requests 
from .utils import fetch, report

### Constants ###

class Next_OT_Op(bpy.types.Operator):
    """ Moves to next mesh """

    bl_idname = "mesh.next"
    bl_label = "Next"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """ Executes the fetching of the next mesh """
        i = context.scene.i + 1
        bpy.ops.object.mode_set(mode='OBJECT')
        if "Loaded" not in context.scene.models: 
            model = context.scene.models.add()
            model.name = "Loaded"
            
        return fetch(self, context, i)
    
class Prev_OT_Op(bpy.types.Operator):
    """ Moves to previous mesh """

    bl_idname = "mesh.prev"
    bl_label = "Prev"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """Executes the segmentation"""
        i = context.scene.i - 1
        bpy.ops.object.mode_set(mode='OBJECT')
        if "Loaded" not in context.scene.models: 
            model = context.scene.models.add()
            model.name = "Loaded"
        return fetch(self, context, i)