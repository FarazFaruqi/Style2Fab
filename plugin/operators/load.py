import bpy
import json
import bmesh
import requests 
import traceback
from .utils import report, domain, fetch

class Load_OT_Op(bpy.types.Operator):
    bl_idname = "mesh.load"
    bl_label = "Load Model"

    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """ Executes the fetching of the next mesh """
        # i = 0 if context.scene.i == context.scene.num_meshes else context.scene.i + 1
        # i = context.scene.i + 1
        i = 3
        if context.object is not None: bpy.ops.object.mode_set(mode='OBJECT')
        if "Loaded" not in context.scene.models: 
            model = context.scene.models.add()
            model.name = "Loaded"
            
        return fetch(self, context, i)