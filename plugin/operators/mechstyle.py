import bpy
import json
import bmesh
import requests 
from .utils import fetch, report

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

        # Retrieve the prompt from the scene properties
        prompt = context.scene.prompt
        print(prompt)
        # Include the prompt in the data you're sending
        data = json.dumps({"prompt": prompt})

        try:
            response = requests.post(url=url, json={"prompt": prompt}).json()
        except Exception as error: 
            self.report({'WARNING'}, f"Error occurred while stylizing mesh\n{report(traceback.format_exc())}")

        return {'FINISHED'}