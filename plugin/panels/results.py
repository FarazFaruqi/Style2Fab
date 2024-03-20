import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class Results_PT_Panel(Panel):
    """
    AF() = a panel for Edit
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Results"
    bl_category = "Mechstyle"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout
        edit_col = layout.column()


        edit_col.row().prop(context.scene, "results_slider")

        label_row = edit_col.row()
        label_row.label(text="0: Original")
        label_row.label(text="1: Max Style")

        edit_col.operator("mesh.mechstyle", icon = "PLUGIN")