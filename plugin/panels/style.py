import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class Style_PT_Panel(Panel):
    """
    AF() = a panel for Stylize
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Stylize"
    bl_category = "Mechstyle"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout

        layout.label(text="Prompt")
        prompt_col = layout.column()
        prompt_row = prompt_col.row()
        prompt_row.prop(context.scene, "prompt")

