import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class Process_PT_Panel(Panel):
    """
    AF() = a panel for Edit
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Process"
    bl_category = "Mechstyle"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout
        edit_col = layout.column()
        edit_row = edit_col.row()
        edit_row.prop(context.scene, "process_dropdown")

        #edit_col = layout.column()
        #edit_row = edit_col.row()
        #edit_row.prop(context.scene, "model_name")

        load_row = layout.row()
        load_col = load_row.column()
        load_col.operator("mesh.load", icon = "PLUGIN")

        #load_row = layout.row()
        #load_col = load_row.column()
        #load_col.operator("mesh.send_to_backend", icon = "PLUGIN")
