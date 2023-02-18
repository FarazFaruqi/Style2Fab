from pickle import TRUE
import bpy
import json
import bmesh
import requests 
from .utils import remove_mesh, add_mesh

### Constants ###
colors = {
    0: ["blue", (0.2549019607843137, 0.4117647058823529, 0.8823529411764706, 1)],
    1: ["violet", (0.5411764705882353, 0.16862745098039217, 0.8862745098039215, 1)],
    2: ["brown", (0.5450980392156862, 0.27058823529411763, 0.07450980392156863, 1)],
    3: ["green", (0.0, 0.5019607843137255, 0.0, 1)],
    4: ["yellow", (1.0, 1.0, 0.0, 1)],
    5: ["red", (0.803921568627451, 0.3607843137254902, 0.3607843137254902, 1)],
    6: ["white", (1.0, 1.0, 1.0, 1)],
    7: ["gray", (0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1)],
    8: ["purple", (0.5019607843137255, 0.0, 0.5019607843137255, 1)],
    9: ["dark blue", (0.09803921568627451, 0.09803921568627451, 0.4392156862745098, 1)],
    10: ["light green", (0.48627450980392156, 0.9882352941176471, 0.0, 1)],
    11: ["gold", (1.0, 0.8431372549019608, 0.0, 1)],
    12: ["blue II", (0.2549019607843137, 0.4117647058823529, 0.8823529411764706, 1)],
    13: ["violet II", (0.5411764705882353, 0.16862745098039217, 0.8862745098039215, 1)],
    14: ["brown II", (0.5450980392156862, 0.27058823529411763, 0.07450980392156863, 1)],
    15: ["green II", (0.0, 0.5019607843137255, 0.0, 1)],
    16: ["yellow II", (1.0, 1.0, 0.0, 1)],
    17: ["red I", (0.803921568627451, 0.3607843137254902, 0.3607843137254902, 1)],
    18: ["white II", (1.0, 1.0, 1.0, 1)],
    19: ["gray II", (0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1)],
    20: ["purple II", (0.5019607843137255, 0.0, 0.5019607843137255, 1)],
    21: ["dark blue II", (0.09803921568627451, 0.09803921568627451, 0.4392156862745098, 1)],
    22: ["light green II", (0.48627450980392156, 0.9882352941176471, 0.0, 1)],
    23: ["gold II", (1.0, 0.8431372549019608, 0.0, 1)],
    24: ["gold III", (1.0, 0.8431372549019608, 0.0, 1)],
}
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class Segment_OT_Op(bpy.types.Operator):
    """ Segment a mesh """

    bl_idname = "mesh.segment_mesh"
    bl_label = "Segment mesh"
    
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

                url = "http://0.0.0.0:8000/segment/"

                data = json.dumps({'vertices': vertices, 'faces': faces, 'k': k, 'collapsed': True, 'remesh': False})

                try:
                    response = requests.post(url = url, json = data).json()
                    
                    faces = response['faces']
                    labels = response['labels']
                    vertices = response['vertices']
                    face_segments = response['face_segments']
                    self.report({'INFO'}, f"Segmented mesh into {k} parts successfully!")
                    
                    mesh_name = obj.name
                    # Remove old mesh   
                    remove_mesh(self, mesh_name)

                    # Add new mesh
                    new_object = add_mesh(self, mesh_name, vertices, faces)

                    self.report({'INFO'}, f"Added new mesh {mesh_name} ...")

                    for stored_models in context.scene.models: 
                        if stored_models.name == mesh_name.lower(): 
                            model = stored_models
                            break
                    else: 
                        model = context.scene.models.add()
                        model.name = mesh_name.lower()
                    model.segmented = True

                    _assign_materials(new_object, k, face_segments, context, labels, model)

                except Exception as error: print(f"Error occured while segmenting mesh\n{report(error)}")
                
            return {'FINISHED'}

### Helper Functions ###
def _assign_materials(mesh, k, face_segments, context, labels, model):
    """ Assigns a colored material for each found segment """
    n = len(face_segments)
    m = len(set(face_segments))
    mesh.data.materials.clear()
    segemnt_to_faces = {i: [] for i in range(m)}
    
    for i in range(n): segemnt_to_faces[face_segments[i]].append(i)

    for i in range(k):
        material = bpy.data.materials.new(''.join(['mat', mesh.name, str(i)]))
        material.diffuse_color = colors[i][1]
        mesh.data.materials.append(material)

        if len(model.segments) <= i: segment = model.segments.add()
        else: segment = model.segments[i]

        segment.i = i
        segment.label = labels[i]
        segment.color = colors[i][0]
        segment.faces = "\n".join(str(j) for j in segemnt_to_faces[i])
        segment.selected = True if segment.label == "function" else False

    for i, label in enumerate(face_segments):
        mesh.data.polygons[i].material_index = int(label)