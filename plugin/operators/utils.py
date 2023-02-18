import bpy
from mathutils import Vector, Matrix

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