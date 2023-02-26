import os
import bpy
import json
import bmesh
import requests

### Constants ###
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

report = lambda error: f"----------------------------\n{error}\n----------------------------\n"
with open(f"{base_dir}/colors.json", "rb") as colors_file:
    colors = json.loads(colors_file.read())['colors']

def remove_mesh(self, mesh_name):
    bpy.ops.object.select_all(action='DESELECT')
    if mesh_name not in bpy.data.objects.keys(): 
        self.report({'INFO'}, f"{mesh_name} not found in {bpy.data.objects.keys()} ...")
        return
    bpy.data.objects[mesh_name].select_set(True)
    bpy.ops.object.delete()
    self.report({'INFO'}, f"Removed old mesh {mesh_name} ...")

def add_mesh(self, mesh_name, vertices, faces):
    new_mesh = bpy.data.meshes.new(mesh_name)
    new_mesh.from_pydata(vertices, [], faces)
    new_mesh.update()

    new_object = bpy.data.objects.new(mesh_name, new_mesh)
    bpy.context.scene.collection.objects.link(new_object)
    bpy.context.view_layer.objects.active = new_object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[mesh_name].select_set(True)

    self.report({'INFO'}, f"Added new mesh {mesh_name} ...")
    return new_object

def fetch(self, context, i):
    mesh_dir = context.scene.mesh_dir

    mesh_name = "Loaded"
    url = "http://0.0.0.0:8000/fetch/"

    data = json.dumps({'i': i, 'mesh_dir': mesh_dir})
    try:
        response = requests.post(url = url, json = data).json()
        
        faces = response['faces']
        labels = response['labels']
        vertices = response['vertices']
        face_segments = response['face_segments']
        self.report({'INFO'}, f"Loaded mesh successfully!")

        context.scene.i = i 
        if faces is None: 
            self.report({'INFO'}, f"No more meshes inside directory {mesh_dir}")
            return {'FINISHED'}

        # Remove old mesh   
        remove_mesh(self, mesh_name)
        context.scene.face_count = len(faces)
        context.scene.vertex_count = len(vertices)

        # Add new mesh
        new_object = add_mesh(self, mesh_name, vertices, faces)

        if labels is not None:
            k = context.scene.num_segs

            for stored_models in context.scene.models: 
                if stored_models.name == mesh_name.lower(): 
                    model = stored_models
                    break
            else: 
                model = context.scene.models.add()
                model.name = mesh_name.lower()
            model.segmented = True

            assign_materials(new_object, k, face_segments, context, labels, model)

    except Exception as error: 
        self.report({'ERROR'}, f"Error occured while fetching mesh\n{report(error)}")
            
    return {'FINISHED'}

def assign_materials(mesh, k, face_segments, context, labels, model):
    """ Assigns a colored material for each found segment """
    if face_segments is None: return
    n = len(face_segments)
    m = len(set(face_segments))
    mesh.data.materials.clear()
    segemnt_to_faces = {i: [] for i in range(m)}
    
    for i in range(n): segemnt_to_faces[face_segments[i]].append(i)

    for i in range(k):
        material = bpy.data.materials.new(''.join(['mat', mesh.name, str(i)]))
        material.diffuse_color = colors[f"{i}"][1]
        mesh.data.materials.append(material)

        if len(model.segments) <= i: segment = model.segments.add()
        else: segment = model.segments[i]

        segment.i = i
        segment.label = labels[i]
        segment.color = colors[f"{i}"][0]
        segment.faces = "\n".join(str(j) for j in segemnt_to_faces[i])
        segment.selected = True if segment.label == "function" else False

    for i, label in enumerate(face_segments):
        mesh.data.polygons[i].material_index = int(label)

def get_segment_vertices(op, context, j):
    """ Gets all vertices of selected segment(s) """
    obj = context.view_layer.objects.active
    mesh = bmesh.from_edit_mesh(obj.data)
    for vertex in mesh.verts:
        vertex.select = False

    vertices = []
    for model in context.scene.models:
        if model.name != obj.name.lower(): continue
        if not model.segmented: continue
        for i in range(len(model.segments)):
            segment = model.segments[i]
            if not segment.selected: continue
            else:
                if i + j == len(model.segments): break
                segment.selected = False
                segment = model.segments[i + j]
                segment.selected = True
                
                faces = list(map(int, segment.faces.split("\n")))
                
                for i in faces:
                    for vertex in obj.data.polygons[i].vertices:
                        vertices.append(vertex)
                break
        break

    return vertices

def select_vertices(context, selected_vertices):
    """ Selects all the vertices in selected_vertices in the UI and unselects all else """
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')

    obj = context.view_layer.objects.active
    mesh = bmesh.from_edit_mesh(obj.data)

    for vertex in mesh.verts:
        if vertex.index in selected_vertices: vertex.select = True
        else: vertex.select = False