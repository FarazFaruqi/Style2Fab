import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class MeshSelection_PT_Panel(Panel):
    """
    AF() = a panel for SmartStyle3D
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Mesh Selector"
    bl_category = "FA3DS"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout

        layout.label(text="Mesh Directory")
        mesh_dir_col = layout.column()
        mesh_dir_row = mesh_dir_col.row()
        mesh_dir_row.prop(context.scene, "mesh_dir")

        edit_row = layout.row()
        edit_col = edit_row.column()
        edit_col_2 = edit_row.column()
        edit_col.operator("mesh.prev_mesh", icon="TRIA_LEFT")
        edit_col_2.operator("mesh.next_mesh", icon = "TRIA_RIGHT")
