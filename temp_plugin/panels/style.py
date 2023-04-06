import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class Something_PT_Panel(Panel):
    """
    AF() = a panel for Segmentation
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Stylize"
    bl_category = "Style2Fab"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout

        layout.label(text="Prompt")
        prompt_col = layout.column()
        prompt_row = prompt_col.row()
        prompt_row.prop(context.scene, "prompt")

        stylize_row = layout.row()
        stylize_col = stylize_row.column()
        stylize_col.operator("mesh.style", icon = "PLUGIN")
