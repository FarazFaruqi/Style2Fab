import bpy
import json
import bmesh
import requests 
from .utils import fetch, report

### Constants ###

class Next_OT_Op(bpy.types.Operator):
    """ Moves to next mesh """

    bl_idname = "mesh.next"
    bl_label = "Load Mesh"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """ Executes the fetching of the next mesh """
        # i = 0 if context.scene.i == context.scene.num_meshes else context.scene.i + 1
        # i = context.scene.i + 1
        i = 0
        if context.object is not None: bpy.ops.object.mode_set(mode='OBJECT')
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
        i = 0 if context.scene.i == 0 else context.scene.i - 1 
        if context.object is not None: bpy.ops.object.mode_set(mode='OBJECT')
        if "Loaded" not in context.scene.models: 
            model = context.scene.models.add()
            model.name = "Loaded"
        return fetch(self, context, i)