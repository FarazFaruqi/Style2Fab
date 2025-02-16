from pickle import TRUE
import bpy
import json
import bmesh
import requests 
import traceback
from .utils import remove_mesh, add_mesh, assign_materials, domain, report

### Constants ###

class Segment_OT_Op(bpy.types.Operator):
    """ Segment a mesh """

    bl_idname = "mesh.segment"
    bl_label = "Process Mesh"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        obj = context.object
        if obj is not None: return True
        print("\033[32m[Error] >> Failed to get model because no object is selected\033[0m")
        
        return False

    def execute(self, context):
        """Executes the segmentation"""
        if bpy.ops.mesh.separate(type='LOOSE') != {'CANCELLED'}:
            self.report({'ERROR'}, "Separated not connected parts, choose one of them for segmentation!")
            return {'CANCELLED'}
        else:
            k = context.scene.num_segs
            objs = [obj for obj in bpy.context.selected_objects]
            for obj in objs:
                vertices = []
                for vertex in obj.data.vertices: vertices.append(vertex.co[:])

                faces = []
                for face in obj.data.polygons: faces.append([i for i in face.vertices])

                url = f"{domain}/segment/"

                meshId = None
                for stored_models in context.scene.models: 
                    if stored_models.name.lower() == obj.name.lower(): 
                        meshId = stored_models.id
                        break

                data = json.dumps({'vertices': vertices, 'faces': faces, 'k': k, 'collapsed': True, 'remesh': False, 'meshId': meshId})

                try:
                    response = requests.post(url = url, json = data).json()
                    
                    k = response['k']
                    faces = response['faces']
                    labels = response['labels']
                    meshId = response['meshId']
                    vertices = response['vertices']
                    face_segments = response['faceSegments']
                    self.report({'INFO'}, f"Segmented mesh into {k} parts successfully!")
                    
                    mesh_name = obj.name
                    # Remove old mesh   
                    remove_mesh(self, mesh_name)

                    # Add new mesh
                    new_object = add_mesh(self, mesh_name, vertices, faces)

                    self.report({'INFO'}, f"Added new mesh {mesh_name} ...")

                    for stored_models in context.scene.models: 
                        if stored_models.name.lower() == mesh_name.lower(): 
                            model = stored_models
                            model.id = meshId
                            break
                    else: 
                        model = context.scene.models.add()
                        model.name = mesh_name.lower()
                        model.id = meshId
                    model.segmented = True
                    self.report({'INFO'}, f"Assigning {k} materials ...")
                    assign_materials(self, new_object, k, face_segments, context, labels, model)

                except Exception as error: print(f"Error occured while segmenting mesh\n{report(traceback.format_exc())}")
                
            return {'FINISHED'}
