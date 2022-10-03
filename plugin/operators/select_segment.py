import bpy
import json
import bmesh
import requests 

### Global Constants ###
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class SelectSegment_OT_Op(bpy.types.Operator):
    """ Segment a mesh """
    bl_idname = "mesh.select_segment"
    bl_label = f"Select"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        obj = context.object
        if obj is not None:
            return True
        print("Failed to get model because no object is selected")
        return False

    def execute(self, context):
        """ Executes the segmentation """
        selected_vertices = [] 
        # deselect everything
        self._select(context, selected_vertices)

        obj = context.view_layer.objects.active
        mesh = bmesh.from_edit_mesh(obj.data)
        for vertex in mesh.verts:
            vertex.select = False

        for segment in context.scene.segments:
            if not segment.selected: continue
            faces = list(map(int, segment.faces.split("\n")))
            
            self.report({'INFO'}, f"{faces}")
            self.report({'INFO'}, f"[{segment.i} selected] >> {segment.selected}")
            for i in faces:
                for vertex in obj.data.polygons[i].vertices:
                    selected_vertices.append(vertex)
        
        # select selected segment
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