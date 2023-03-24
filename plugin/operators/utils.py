import os
import bpy
import json
import bmesh
import json
import requests
import traceback

### Constants ###
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(f"{base_dir}/settings.json", 'r') as ip_file:  
    ip_file = json.load(ip_file)
    domain = f"http://{ip_file['ip']}:{ip_file['port']}"

report = lambda error: f"\033[31m----------------------------\n{error}\n----------------------------\033[0m\n"
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

    mesh_prefix = "Loaded"
    url = f"{domain}/fetch/"

    data = json.dumps({'i': i, 'mesh_dir': mesh_dir})
    try:
        response = requests.post(url = url, json = data).json()
        
        failed = response['failed']
        meshIds = response['meshIds']
        faces_list = response['faces']
        labels_list = response['labels']
        num_meshes = response['numMeshes']
        vertices_list = response['vertices']
        face_segments_list = response['face_segments']
        self.report({'INFO'}, f"Loaded mesh successfully!")

        context.scene.i = i 
        context.scene.num_meshes = num_meshes
        if failed: 
            self.report({'WARNING'}, f"Failed to load mesh {i}")
            return {'FINISHED'}
        
        if len(faces_list) == 0: 
            self.report({'INFO'}, f"No more meshes inside directory {mesh_dir}")
            return {'FINISHED'}

        for i in range(1000): 
            try: remove_mesh(self, f"{mesh_prefix}_{i}")
            except: continue

        for i in range(len(meshIds)):
            meshId = meshIds[i]
            faces = faces_list[i]
            labels = labels_list[i]
            vertices = vertices_list[i]
            face_segments = face_segments_list[i]

            mesh_name = f"{mesh_prefix}_{i}"
            # Remove old mesh   
            remove_mesh(self, mesh_name)
            context.scene.face_count = len(faces)
            context.scene.vertex_count = len(vertices)

            # Add new mesh
            new_object = add_mesh(self, mesh_name, vertices, faces)

            if face_segments is not None:
                k = len(set(face_segments))

                for stored_models in context.scene.models: 
                    if stored_models.name == mesh_name.lower(): 
                        model = stored_models
                        model.id = meshId
                        break
                else: 
                    model = context.scene.models.add()
                    model.name = mesh_name.lower()
                    model.id = meshId
                model.segmented = True
                assign_materials(self, new_object, k, face_segments, context, labels, model)
                self.report({'INFO'}, f"[labels] >> {len(labels)} == {k} {labels}")

    except Exception as error: 
        self.report({'ERROR'}, f"Error occured while fetching mesh\n{report(traceback.format_exc())}")
            
    return {'FINISHED'}

def assign_materials(self, mesh, k, face_segments, context, labels, model):
    """ Assigns a colored material for each found segment """
    if face_segments is None: return
    n = len(face_segments)
    m = len(set(face_segments))
    mesh.data.materials.clear()
    segemnt_to_faces = {i: [] for i in range(m)}
    
    for i in range(n): segemnt_to_faces[face_segments[i]].append(i)
    
    for i in range(k):
        self.report({'INFO'}, f"Assigning material {i} ...")
        material = bpy.data.materials.new(''.join(['mat', mesh.name, str(i)]))
        material.diffuse_color = colors[f"{i}"][1]
        mesh.data.materials.append(material)

        if len(model.segments) <= i: segment = model.segments.add()
        else: segment = model.segments[i]

        segment.i = i
        segment.label = labels[i].lower()
        segment.color = colors[f"{i}"][0]
        segment.faces = "\n".join(str(j) for j in segemnt_to_faces[i])
        segment.is_form = True if segment.label == "form" else False
        segment.is_func = True if segment.label == "function" else False

        vertex_map = {}
        face_matrix = []
        vertex_matrix = []
        for j in segemnt_to_faces[i]:
            face = []
            for vertex in mesh.data.polygons[j].vertices: 
                if vertex not in vertex_map:
                    vertex_map[vertex] = len(vertex_matrix)
                    vertex_matrix.append(mesh.data.vertices[vertex].co[:])
                face.append(vertex_map[vertex])
            face_matrix.append(face)

        segment.vertex_matrix = json.dumps(vertex_matrix)
        segment.face_matrix = json.dumps(face_matrix)

    for i, label in enumerate(face_segments):
        mesh.data.polygons[i].material_index = int(label)

def get_segment_vertices(self, context, j):
    """ Gets all vertices of selected segment(s) """
    obj = context.view_layer.objects.active
    mesh = bmesh.from_edit_mesh(obj.data)

    for vertex in mesh.verts:
        vertex.select = False

    vertices = None
    for model in context.scene.models:
        if model.name != obj.name.lower(): continue
        if not model.segmented: continue
        for i in range(len(model.segments)):
            segment = model.segments[i]
            self.report({'INFO'}, f"[segemnt {i}] >> selected? {segment.selected}")
            if not segment.selected: continue
            else:
                if (i + j == len(model.segments)) or (i + j < 0): break
                segment.selected = False
                if vertices is None: vertices = extract_vertices(model, obj, i + j)
                else: vertices += extract_vertices(model, obj, i + j)
                
                if j != 0: break
        if vertices is None:
            vertices = extract_vertices(model, obj, 0)
        if j != 0: break

    return vertices
    
def extract_vertices(model, obj, j):
    segment = model.segments[j]
    segment.selected = True
    
    vertices = []
    faces = list(map(int, segment.faces.split("\n")))

    for i in faces:
        for vertex in obj.data.polygons[i].vertices:
            vertices.append(vertex)
    
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