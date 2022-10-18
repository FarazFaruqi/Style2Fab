import bpy
import json
import bmesh
import requests 

### Global Constants ###
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class ShowModelInfoForm_OT_Op(bpy.types.Operator):
    """ Displays model info """
    bl_idname = "mesh.show_mesh_info_form"
    bl_label = f"Select"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        objs = context.selected_objects
        if len(objs) == 1: return True
        print("Failed to get model because no object is selected")
        return False

    def execute(self, context):
        """ Executes the segmentation """
        obj = context.view_layer.objects.active

        for model in context.scene.models:
            if model.name != obj.name.lower(): continue
            model.show_form = not model.show_form

        return {'FINISHED'}

class ShowModelInfoFunction_OT_Op(bpy.types.Operator):
    """ Displays model info """
    bl_idname = "mesh.show_mesh_info_function"
    bl_label = f"Select"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        objs = context.selected_objects
        if len(objs) == 1: return True
        print("Failed to get model because no object is selected")
        return False

    def execute(self, context):
        """ Executes the segmentation """
        obj = context.view_layer.objects.active

        for model in context.scene.models:
            if model.name != obj.name.lower(): continue
            model.show_function = not model.show_function

        return {'FINISHED'}