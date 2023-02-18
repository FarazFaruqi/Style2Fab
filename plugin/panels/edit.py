import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class Edit_PT_Panel(Panel):
    """
    AF() = a panel for Edit
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Edit"
    bl_category = "FA3DS"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout
        edit_col = layout.column()
        edit_row = edit_col.row()
        edit_row.prop(context.scene, "mode")

        edit_row = layout.row()
        edit_col = edit_row.column()
        edit_col.operator("mesh.edit_mesh", icon = "PLUGIN")
