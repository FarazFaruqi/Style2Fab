import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class Select_PT_Panel(Panel):
    """
    AF() = a panel for Segmentation
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Style2Fab"
    bl_category = "Style2Fab"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout
        layout.label(text=f"Selected Model ({context.scene.codedModels.capitalize()})")
        model_col = layout.column()
        model_row = model_col.row()
        model_row.prop(context.scene, "codedModels")

### Helper Functions ###