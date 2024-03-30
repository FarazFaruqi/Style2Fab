import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class Settings_PT_Panel(Panel):
    """
    AF() = a panel for Edit
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Simulation Settings"
    bl_category = "Mechstyle"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout
        edit_col = layout.column()

        edit_col.row().prop(context.scene, "settings_materials_dropdown")

        edit_col.separator()
        #edit_col.row().prop(context.scene, "settings_slider")
        edit_col.row().prop(context.scene, "settings_radio", expand=True)