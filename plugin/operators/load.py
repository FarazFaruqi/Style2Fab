import bpy
import json
import bmesh
import requests 
import traceback
from .utils import report, domain, fetch

class Load_OT_Op(bpy.types.Operator):
    bl_idname = "mesh.load"
    bl_label = "Load Model"
    bl_description = "Loads model before stylization for mask selection in edit mode based on Model Dropdown"

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
            
        return fetch(self, "dropdown", context, i)
    
class Load_Final_OT_Op(bpy.types.Operator):
    bl_idname = "mesh.load_final"
    bl_label = "Load Model"
    bl_description = "Loads stylized model based on Model Name and color selection"

    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """ Executes the fetching of the next mesh """
        i = 3
        if context.object is not None: bpy.ops.object.mode_set(mode='OBJECT')
        if "Loaded" not in context.scene.models: 
            model = context.scene.models.add()
            model.name = "Loaded"
            
        # Use the value from the property 'model_name' in the scene
        model_name = context.scene.model_name
        model_dir = f"/home/ubuntu/MechStyle-code/Models/Blender_Export/{model_name}/{model_name}_current.obj"


        if context.scene.results_radio == "Stylized":
            color_type = "colors"
        elif context.scene.results_radio == "FEA":
            color_type = "stress_values"
        else:
            # else shouldn't ever be called, but just in case something goes wrong it will fail silently 
            color_type = None

        return fetch(self, model_dir, context, i, color_type=color_type)
    
class Load_Paper_OT_Op(bpy.types.Operator):
    bl_idname = "mesh.load_paper"
    bl_label = "Load Model"
    bl_description = "Loads stylized model with texture or stress values"

    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """ Executes the fetching of the next mesh """
        i = 3
        if context.object is not None: bpy.ops.object.mode_set(mode='OBJECT')
        if "Loaded" not in context.scene.models: 
            model = context.scene.models.add()
            model.name = "Loaded"
            
        # Use the value from the property 'model_name' in the scene
        model_name = context.scene.model_name
        model_dir = "/home/ubuntu/MechStyle-code/Models/Hook_Paper_Example/hook_mechstyle.obj"


        if context.scene.results_radio == "Stylized":
            color_type = "colors"
        elif context.scene.results_radio == "FEA":
            color_type = "stress_values"
        else:
            # else shouldn't ever be called, but just in case something goes wrong it will fail silently 
            color_type = None

        return fetch(self, model_dir, context, i, color_type=color_type)
    
