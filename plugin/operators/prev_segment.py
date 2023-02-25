import bpy
import json
import bmesh
import requests 
from .utils import remove_mesh, add_mesh, fetch

### Constants ###
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class PrevSeg_OT_Op(bpy.types.Operator):
    """ Moves to previous mesh """

    bl_idname = "mesh.prev_segment"
    bl_label = "prev"
    
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
        self._select(context, selected_vertices)

        obj = context.view_layer.objects.active
        mesh = bmesh.from_edit_mesh(obj.data)
        for vertex in mesh.verts:
            vertex.select = False

        for model in context.scene.models:
            if model.name != obj.name.lower(): continue
            if not model.segmented: continue
            for i in range(len(model.segments)):
                segment = model.segments[i]
                if not segment.selected: continue
                else:
                    if i - 1 < 0: break
                    segment.selected = False
                    segment = model.segments[i - 1]
                    segment.selected = True
                    
                    faces = list(map(int, segment.faces.split("\n")))
                    
                    self.report({'INFO'}, f"{faces}")
                    self.report({'INFO'}, f"[{segment.i} selected] >> {segment.selected}")
                    for i in faces:
                        for vertex in obj.data.polygons[i].vertices:
                            selected_vertices.append(vertex)
                    break
            break
        
        self._select(context, selected_vertices)

        return {'FINISHED'}
    
    def _select(self, context, selected_vertices):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        obj = context.view_layer.objects.active
        mesh = bmesh.from_edit_mesh(obj.data)

        for vertex in mesh.verts:
            if vertex.index in selected_vertices: vertex.select = True
            else: vertex.select = False