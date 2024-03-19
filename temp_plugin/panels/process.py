import bpy
from bpy.types import Panel

### Global Constants ###

class Process_PT_Panel(Panel):
    """
    AF() = a panel for Model Selection
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Process"
    bl_category = "Style2Fab"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout

        layout.label(text="Model Location")

