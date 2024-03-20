import bpy
import json
import bmesh
import requests 
import traceback
from .utils import report, domain, fetch

class Send_OT_Op(bpy.types.Operator):
    '''
        Send current model to be saved in server
    '''
    
    bl_idname = "mesh.send_to_backend"
    bl_label = "Save Current Model in Backend"

    @classmethod
    def poll(cls, context):
        """ Indicates whether the operator should be enabled """
        obj = context.object
        if obj is not None and obj.mode == "EDIT": return True
        print("\033[32m[Error] >> Failed to stylize model because object is not in edit mode\033[0m")
        
        return False

    def execute(self, context):
        """ Executes the fetching of the selected mesh to backend """
        objs = [obj for obj in bpy.context.selected_objects]

        faces = []
        vertices = []
        selection = []
        for obj in objs:
            n = len(vertices)
            for i, vertex in enumerate(obj.data.vertices): 
                vertices.append(vertex.co[:])

            for face in obj.data.polygons: 
                faces.append([n + i for i in face.vertices])

            mesh = bmesh.from_edit_mesh(obj.data)
            for i, vertex in enumerate(mesh.verts):
                if vertex.select: selection.append(n + i)

        url = f"{domain}/save_model/"
        
        #data = json.dumps({'vertices': vertices, 'faces': faces, 'prompt': prompt, 'selection': selection, 'remesh': False, "index": context.scene.i, "model": "r"})
        data = json.dumps({'vertices': vertices, 'faces': faces})

        try:
            response = requests.post(url = url, json = data).json()
        except Exception as error: 
            self.report({'WARNING'}, f"Error occurred while saving mesh\n{report(traceback.format_exc())}")

        return {'FINISHED'}