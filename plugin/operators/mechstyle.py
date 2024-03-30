import bpy
import json
import bmesh
import requests 
from .utils import fetch, add_mesh, report, domain, traceback, remove_mesh

class Mechstyle_OT_Op(bpy.types.Operator):
    bl_idname = "mesh.mechstyle"
    bl_label = "Stylize"

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
        selection_vertices = []

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
        
        print(selection_vertices)

        

        try:
            response = requests.post(url=url, json={"prompt": prompt, "selection": selection, "vertices": vertices, "mesh_dir": mesh_dir, "name": model_name}).json()
            
            colors = response['colors']
            faces = response['faces']
            vertices = response['vertices']
            self.report({'INFO'}, f"Loaded mesh successfully!")
  

            mesh_name = model_name
            meshId = "0"
            context.scene.loaded += f"{mesh_name}"

            # Remove old mesh   
            remove_mesh(self, mesh_name)
            context.scene.face_count = len(faces)
            context.scene.vertex_count = len(vertices)

            # Add new mesh
            new_object = add_mesh(self, mesh_name, vertices, faces, colors, vertex_normals=None)

            model = context.scene.models.add()
            model.name = mesh_name.lower()
            model.id = meshId

            context.scene.stylization_loss = "0.123"  # Update with actual value
            context.scene.structural_loss = "0.456"  # Update with actual value
        except Exception as error:
            self.report({'WARNING'}, f"Error occurred while stylizing mesh\n{report(traceback.format_exc())}")

        return {'FINISHED'}