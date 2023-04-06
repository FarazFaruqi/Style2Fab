import bpy
import json
import bmesh
import requests 

### Constants ###

class Next_OT_Op(bpy.types.Operator):
    """ Moves to next segment """

    bl_idname = "seg.next"
    bl_label = "Next"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """Executes the segmentation"""
        return {'FINISHED'}

class Prev_OT_Op(bpy.types.Operator):
    """ Moves to previous segment """

    bl_idname = "seg.prev"
    bl_label = "Previous"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """Executes the segmentation"""
        return {'FINISHED'}

class Func_OT_Op(bpy.types.Operator):
    """ Moves to previous segment """

    bl_idname = "seg.select_func"
    bl_label = "Highlight Functional Segments"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """Executes the segmentation"""
        return {'FINISHED'}