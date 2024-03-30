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

def add_mesh(self, mesh_name, vertices, faces, colors, vertex_normals=None):
    new_mesh = bpy.data.meshes.new(mesh_name)
    new_mesh.from_pydata(vertices, [], faces)
    new_mesh.update()

    new_object = bpy.data.objects.new(mesh_name, new_mesh)
    bpy.context.scene.collection.objects.link(new_object)

    # Create a vertex color map
    color_layer = new_mesh.vertex_colors.new(name="Col")
    
    # Fill the vertex color map
    for poly in new_mesh.polygons:
        for loop_index, vertex_index in zip(poly.loop_indices, poly.vertices):
            loop_vert_color = color_layer.data[loop_index]
            loop_vert_color.color = (*colors[vertex_index], 1.0)  # add alpha

    bpy.context.view_layer.objects.active = new_object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[mesh_name].select_set(True)

    # Create a material that uses the vertex colors
    material = bpy.data.materials.new(name=f"{mesh_name}_Material")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    assert bsdf is not None, "Failed to find Principled BSDF node"

    # Create an attribute node to fetch the vertex colors and connect it
    attr_node = material.node_tree.nodes.new('ShaderNodeAttribute')
    attr_node.attribute_name = 'Col'  # The name of your vertex color layer
    material.node_tree.links.new(attr_node.outputs['Color'], bsdf.inputs['Base Color'])

    # Assign the material to the object
    if len(new_object.data.materials) == 0:
        new_object.data.materials.append(material)
    else:
        new_object.data.materials[0] = material

    self.report({'INFO'}, f"Added new mesh {mesh_name} ...")
    return new_object


def fetch(self, mesh_dir, context, i, color_type=None):
    # Fetching 'in progress' models leads to broken results, however 'modelname_current.obj' imports correctly
    if mesh_dir == "dropdown":
        mesh_dir = context.scene.process_dropdown
    #mesh_dir = "/home/ubuntu/MechStyle-code/Models/Blender_Export/hook_2/hook_2_current.obj"
    #mesh_dir = "/home/ubuntu/MechStyle-code/Models/Blender_Export/bag_clip/bag_clip_199.obj"
    #mesh_dir = "/home/ubuntu/MechStyle-code/Models/Examples/Bag_Clip_Test_No_stylization_9/bag_clip_current.obj"
    print("Selected mesh directory:", mesh_dir)

    mesh_prefix = "Loaded"
    url = f"{domain}/fetch/"

    data = json.dumps({'i': i, 'mesh_dir': mesh_dir, 'color_type': color_type})
    try:
        response = requests.post(url = url, json = data).json()
        
        failed = response['failed']
        colors = response['colors']
        meshIds = response['meshIds']
        faces_list = response['faces']
        vertex_normals_list = response['vertex_normals']
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

        for name in context.scene.loaded.split(","): 
            try: remove_mesh(self, name)
            except: continue

        context.scene.loaded = ""
        for i in range(len(meshIds)):
            meshId = meshIds[i]
            faces = faces_list[i]
            vertex_normals = vertex_normals_list[i]
            labels = labels_list[i]
            vertices = vertices_list[i]
            face_segments = face_segments_list[i]
            colors = colors[i]

            mesh_name = f"{meshId.split('/')[-1]}"
            context.scene.loaded += f"{mesh_name}"
            if i < len(meshId) - 1: context.scene.loaded += ","
            # Remove old mesh   
            remove_mesh(self, mesh_name)
            context.scene.face_count = len(faces)
            context.scene.vertex_count = len(vertices)

            # Add new mesh
            new_object = add_mesh(self, mesh_name, vertices, faces, colors, vertex_normals)

            model = context.scene.models.add()
            model.name = mesh_name.lower()
            model.id = meshId

            #if face_segments is not None:
            #    k = len(set(face_segments))

            #    for stored_models in context.scene.models: 
            #        if stored_models.name == mesh_name.lower(): 
            #            model = stored_models
            #            model.id = meshId
            #            break
            #    else: 
            #        model = context.scene.models.add()
            #        model.name = mesh_name.lower()
            #        model.id = meshId
            #    model.segmented = True
            #    assign_materials(self, new_object, k, face_segments, context, labels, model)
            #    self.report({'INFO'}, f"[labels] >> {len(labels)} == {k} {labels}")

    except Exception as error: 
        self.report({'ERROR'}, f"Error occured while fetching mesh\n{report(traceback.format_exc())}")
            
    return {'FINISHED'}

def fetch_sim(self, context, i):
    mesh_set = []
    for obj in bpy.context.selected_objects:
        for model in context.scene.models:
            if obj.name.lower() == model.name.lower(): mesh_set.append(model.id)

    try:
        data = json.dumps({'meshSet': mesh_set, "t": context.scene.t, "i": i})

        url = f"{domain}/assemble/fetchSimilarity"
        response = requests.post(url = url, json = data).json()
        similarity = response['similarity']

        if similarity is None: return {"FINISHED"}

        model_id, other_id, i, j, sim = similarity

        found = 0
        for model in context.scene.models:
            if model.id.lower() == model_id.lower():
                model.segment_enum = f"{i}" if found == 0 else f"{j}" 
                found += 1
            if found == 2: break
        
        context.scene.assembly_enums[0].model_enum = model_id.split("/")[-1].lower()
        context.scene.assembly_enums[1].model_enum = other_id.split("/")[-1].lower()

        context.scene.similarity.add()
        context.scene.similarity[-1].i = int(i)
        context.scene.similarity[-1].j = int(j)
        context.scene.similarity[-1].sim = float(sim)
        context.scene.similarity[-1].model_id = model_id.lower()
        context.scene.similarity[-1].other_id = other_id.lower()

        self.report({'INFO'}, f"[response] >> {response}")
    except: self.report({'ERROR'}, f"Error occured while assembleing mesh\n{report(traceback.format_exc())}")

    return {"FINISHED"}

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

def get_segment_vertices(self, context, j, obj = None):
    """ Gets all vertices of selected segment(s) """
    if obj is None: obj = context.view_layer.objects.active
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

def select_vertices(context, selected_vertices, obj = None):
    """ Selects all the vertices in selected_vertices in the UI and unselects all else """
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')

    if obj is None: obj = context.view_layer.objects.active
    mesh = bmesh.from_edit_mesh(obj.data)

    for vertex in mesh.verts:
        if vertex.index in selected_vertices: vertex.select = True
        else: vertex.select = False