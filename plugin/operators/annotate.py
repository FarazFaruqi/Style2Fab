import bpy
import json
import bmesh
import requests 
from .utils import report

### Constants ###
form = "Form"
func = "Function"

class Annotate_OT_Op(bpy.types.Operator):
    """ Annotates a mesh by storing the labels """

    bl_idname = "mesh.annotate"
    bl_label = "annotate"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        objs = context.selected_objects
        if len(objs) == 1: return True
        print("Failed to get model because no object is selected")
        return False

    def execute(self, context):
        """ Executes the annotation """
        url = "http://0.0.0.0:8000/classify/annotate"
        objs = [obj for obj in bpy.context.selected_objects]
        for obj in objs:
            for stored_model in context.scene.models: 
                if stored_model.name.lower() == obj.name.lower():
                    if not stored_model.segmented: continue
                    labels = []
                    for segment in stored_model.segments:
                        if segment.is_form and segment.is_func: 
                            self.reprot({'ERROR'}, f"Segment can not be both function and form!")
                            return {'FINISHED'}
                         
                        if segment.is_form: labels.append(form)
                        elif segment.is_func: labels.append(func)
                        
                    data = json.dumps({'meshId': stored_model.id, 'labels': labels})

                    try:
                        response = requests.post(url = url, json = data).json()
                        
                        self.report({'INFO'}, f"Annotated mesh successfully!")

                    except Exception as error: self.report({'ERROR'}, f"Error occured while editing mesh\n{report(error)}")

        return {'FINISHED'}