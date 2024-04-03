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


        #edit_col.row().prop(context.scene, "results_slider")
        #label_row = edit_col.row()
        #label_row.label(text="0: Original")
        #label_row.label(text="1: Max Style")

        edit_col.row().prop(context.scene, "results_radio", expand=True)

        load_row = edit_col.row()
        load_col = load_row.column()
        #load_col.operator("mesh.load_final", icon = "PLUGIN")
        load_col.operator("mesh.load_paper", icon = "PLUGIN")

        # Add the stylization and structural loss labels
        edit_col.label(text=f"Stylization: {context.scene.stylization_loss}")
        edit_col.label(text=f"Max Structural Stress Change: {context.scene.structural_loss}")
