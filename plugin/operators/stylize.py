import bpy
import json
import bmesh
import requests 
import traceback
from .utils import report, domain

### Constants ###

class Stylize_OT_Op(bpy.types.Operator):
    """ Segment a mesh """

    bl_idname = "mesh.stylize"
    bl_label = "Stylize"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        obj = context.object
        if obj is not None and obj.mode == "EDIT": return True
        print("\033[32m[Error] >> Failed to stylize model because object is not in edit mode\033[0m")
        
        return False

    def execute(self, context):
        """Executes the segmentation"""
        prompt = context.scene.prompt
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

        url = f"{domain}/stylize/"
        self.report({'INFO'}, f"Stylizing {len(objs)} meshes with {len(faces)} faces and {len(vertices)} vertices ...")
        
        data = json.dumps({'vertices': vertices, 'faces': faces, 'prompt': prompt, 'selection': selection, 'remesh': False, "index": context.scene.i})
        
        try:
            response = requests.post(url = url, json = data).json()
            faces = response['faces']
            vertices = response['vertices']
            materials = response['materials']
            self.report({'INFO'}, f"Stylized mesh successfully!")
            
            mesh_name = f"{obj.name}_stylized"
            new_mesh = bpy.data.meshes.new(mesh_name)
            new_mesh.from_pydata(vertices, [], faces)
  
            new_mesh.update()
            new_object = bpy.data.objects.new(mesh_name, new_mesh)
            bpy.context.scene.collection.objects.link(new_object)
            bpy.context.view_layer.objects.active = new_object

            self.report({'INFO'}, f"Added new mesh {mesh_name} ...")
                          
            _assign_materials(new_object, materials)

            bpy.ops.object.mode_set(mode='OBJECT')

        except Exception as error: self.report({'WARNING'}, f"Error occured while stylizing mesh\n{report(traceback.format_exc())}")
        
        return {'FINISHED'}

### Helper Functions ###
def _assign_materials(mesh, colors):
    """ 
    Stylizes a mesh given a set of materials of size f x 4 where every element 
    indicates cooresponding material color 

    Inputs
        :mesh: <bpy.opes.Mesh> representing the object to be displayed
        :materials: <list> of size f x 4, where f is number of faces in mesh
    """
    j = 0
    taken = {}
    for i, color in enumerate(colors):
        if tuple(color) not in taken:
            j += 1
            taken[tuple(color)] = j
            material = bpy.data.materials.new(''.join(['mat', mesh.name, str(j)]))
            material.diffuse_color = color
            mesh.data.materials.append(material)

        mesh.data.polygons[i].material_index = taken[tuple(color)]
    
        