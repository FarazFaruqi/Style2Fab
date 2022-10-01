import bpy
import json
import bmesh
import requests 

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
    11: ["gold", (1.0, 0.8431372549019608, 0.0, 1)]
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
            k = 12
            obj = context.view_layer.objects.active
            selected_mesh = context.scene.selected_mesh
            
            vertices = []
            for vertex in obj.data.vertices: vertices.append(vertex.co[:])

            faces = []
            for face in obj.data.polygons: faces.append([i for i in face])

            url = "http://0.0.0.0:8000/imad/segment"
            
            data = json.dumps({'vertices': vertices, 'faces': faces, 'k': k, 'collapsed': True})

            try:
                response = requests.post(url = url, json = data).json()
                
                labels = response['labels']
                face_segments = response['face_segments']

                self.report({'INFO'}, f"Segmented mesh into {k} parts successfully!")
                _assign_materials(obj, k, face_segments, context, labels)

            except Exception as error: raise error; print(f"Error occured while segmenting mesh\n{report(error)}")
            
            return {'FINISHED'}

### Helper Functions ###
def _assign_materials(mesh, k, face_segments, context, labels):
    """ Assigns a colored material for each found segment """
    n = len(face_segments)
    m = len(set(face_segments))
    mesh.data.materials.clear()
    segemnt_to_faces = {i: [] for i in range(m)}
    
    for i in range(n): segemnt_to_faces[face_segments[i]].append(i)
    print(f"I found {m} labels!")

    for i in range(k):
        material = bpy.data.materials.new(''.join(['mat', mesh.name, str(i)]))
        material.diffuse_color = colors[i][1]
        mesh.data.materials.append(material)

        if len(context.scene.segments) <= i: segment = context.scene.segments.add()
        else: segment = context.scene.segments[i]

        segment.i = i
        segment.label = labels[i]
        segment.color = colors[i][0]
        segment.faces = "\n".join(str(j) for j in segemnt_to_faces[i])
        segment.selected = True if segment.label == "function" else False

    for i, label in enumerate(face_segments):
        mesh.data.polygons[i].material_index = int(label)