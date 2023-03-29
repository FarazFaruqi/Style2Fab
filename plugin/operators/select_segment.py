import bpy
import json
import bmesh
import requests 
from .utils import get_segment_vertices, select_vertices, report

### Constants ###

class NextSeg_OT_Op(bpy.types.Operator):
    """ Moves to next segment """

    bl_idname = "segment.next"
    bl_label = "Next"
    
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
        self.report({'INFO'}, f"{len(selected_vertices)} vertices selected")
        select_vertices(context, selected_vertices)

        return {'FINISHED'}

class PrevSeg_OT_Op(bpy.types.Operator):
    """ Moves to previous segment """

    bl_idname = "segment.prev"
    bl_label = "Prev"
    
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
        selected_vertices += get_segment_vertices(self, context, -1)
        self.report({'INFO'}, f"{len(selected_vertices)} vertices selected")
        select_vertices(context, selected_vertices)

        return {'FINISHED'}

class SelectFunc_OT_Op(bpy.types.Operator):
    """ Moves to previous segment """

    bl_idname = "segment.select_func"
    bl_label = "Select all function"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        objs = context.selected_objects
        if len(objs) >= 1: return True
        print("Failed to get model because no object is selected")
        return False

    def execute(self, context):
        """Executes the segmentation"""
        objs = [obj for obj in bpy.context.selected_objects]

        for obj in objs:
            selected_vertices = [] 
            # deselect everything
            select_vertices(context, selected_vertices, obj)

            num_func = 0
            for model in context.scene.models:
                if model.name != obj.name.lower(): continue
                if not model.segmented: continue
                self.report({'INFO'}, f"Found {obj.name} == {model.name}")
                for i in range(len(model.segments)):
                    segment = model.segments[i]
                    if segment.is_func: segment.selected = True; num_func += 1
                    else: segment.selected = False
                break

            if num_func > 0: selected_vertices += get_segment_vertices(self, context, 0, obj)
            
            select_vertices(context, selected_vertices, obj)

        return {'FINISHED'}
    