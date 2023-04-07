import bpy
import json
import bmesh
import requests 
import traceback
from bpy.props import EnumProperty
from .utils import *

### Constants ###

class Similarity_OT_Op(bpy.types.Operator):
    """ Similarity between mesh segments """

    bl_idname = "mesh.similarity"
    bl_label = "Similarity"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        obj = context.object
        if obj is not None: return True
        print("\033[32m[Error] >> Failed to get model because no object is selected\033[0m")
        
        return False

    def execute(self, context):
        """Executes the segmentation"""
        try:
            if len(context.scene.assembly_enums) == 0:
                context.scene.assembly_enums.add()
                context.scene.assembly_enums.add()

            found = 0
            mesh_set = []

            assembly_enums = context.scene.assembly_enums
            for model in context.scene.models:
                selected_vertices = []
                self.report({'INFO'}, f"[model name] >> {model.name}")
                if (f"{model.name.lower()}" == assembly_enums[0].model_enum) or \
                   (f"{model.name.lower()}" == assembly_enums[1].model_enum):
                    selected_obj = None
                    for obj in bpy.context.selected_objects:
                        if obj.name.lower() == model.name.lower(): selected_obj = obj; break

                    # deselect everything
                    select_vertices(context, selected_vertices, selected_obj)

                    if selected_obj is not None:
                        for j, segment in enumerate(model.segments):
                            if (f"{segment.i}" == model.segment_enum) or \
                                (f"{segment.i}" == model.segment_enum):
                                mesh_set.append((model.id, segment.i, json.loads(segment.face_matrix), json.loads(segment.vertex_matrix)))
                                found += 1
                                segment.selected = True
                            else: segment.selected = False
                            # if found == 2: break
                        selected_vertices += get_segment_vertices(self, context, 0, selected_obj)
                        select_vertices(context, selected_vertices, selected_obj)
                    # if found == 2: break
            
            data = json.dumps({'meshSet': mesh_set})

            url = f"{domain}/assemble/"
            response = requests.post(url = url, json = data).json()
            
            similarities = response['similarities']
            for key, val in similarities.items():
                for other in val:
                    model_id, i = key.split(",")
                    (other_id, j), sim = other
                    context.scene.similarity.add()

                    context.scene.similarity[-1].i = int(i)
                    context.scene.similarity[-1].j = int(j)
                    context.scene.similarity[-1].sim = float(sim)
                    context.scene.similarity[-1].model_id = model_id.lower()
                    context.scene.similarity[-1].other_id = other_id.lower()
            
            self.report({'INFO'}, f"{len(selected_vertices)} vertices selected")
            self.report({'INFO'}, f"Computed similarities successfully!")
  
        except Exception as error: self.report({'ERROR'}, f"Error occured while assembleing mesh\n{report(traceback.format_exc())}")
        
        return {'FINISHED'}

class NextSim_OT_Op(bpy.types.Operator):
    """ Moves to next similarity above threshold """

    bl_idname = "mesh.next_sim"
    bl_label = "Next"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """Executes the segmentation"""
        context.scene.sim_i += 1
        return fetch_sim(self, context, context.scene.sim_i)
        
class PrevSim_OT_Op(bpy.types.Operator):
    """ Moves to previous similarity above threshold """

    bl_idname = "mesh.prev_sim"
    bl_label = "Prev"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """Executes the segmentation"""
        context.scene.sim_i = max(0, context.scene.sim_i -1)
        return fetch_sim(self, context, context.scene.sim_i)
    
### Helper Functions ##