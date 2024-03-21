import bpy
import json
import bmesh
import requests 
from .utils import fetch, report, domain, traceback

class Mechstyle_OT_Op(bpy.types.Operator):
    bl_idname = "mesh.mechstyle"
    bl_label = "Mechstyle"

    @classmethod
    def poll(cls, context):
        """ Indicates whether the operator should be enabled """
        return True
    
    def execute(self, context):
        """Executes mechstyle"""
        url = f"{domain}/mechstyle/"

        mesh_dir = context.scene.process_dropdown
        model_name = context.scene.model_name

        # pass in model selection to mask out weights
        objs = [obj for obj in bpy.context.selected_objects]
        selection = []
        vertices = []

        for obj in objs:
            n = len(vertices)
            for i, vertex in enumerate(obj.data.vertices): 
                vertices.append(vertex.co[:])

            mesh = bmesh.from_edit_mesh(obj.data)
            for i, vertex in enumerate(mesh.verts):
                if vertex.select: selection.append(n + i)

        # Retrieve the prompt from the scene properties
        prompt = context.scene.prompt

        # Include the prompt and selection
        #data = json.dumps({"prompt": prompt, "selection": selection})
        
        print(selection)

        try:
            response = requests.post(url=url, json={"prompt": prompt, "selection": selection, "vertices": vertices, "mesh_dir": mesh_dir, "name": model_name}).json()
        except Exception as error:
            self.report({'WARNING'}, f"Error occurred while stylizing mesh\n{report(traceback.format_exc())}")

        return {'FINISHED'}