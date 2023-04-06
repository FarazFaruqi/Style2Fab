import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class Similar_PT_Panel(Panel):
    """
    AF() = a panel for Similarity
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Assembly"
    bl_category = "Style2Fab"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout

        layout.label(text="Single Component")
        layout.label(text="Similarity: 0.829")

        mesh_row = layout.row()

        mesh_col_1 = mesh_row.column()
        mesh_col_2 = mesh_row.column()

        mesh_col_1.prop(context.scene, "model_1")
        mesh_col_2.prop(context.scene, "model_2")

        stylize_row = layout.row()
        stylize_col = stylize_row.column()
        stylize_col.operator("mesh.sim", icon = "PLUGIN")

        sim_row = layout.row()
        sim_col = sim_row.column()
        sim_col_2 = sim_row.column()
        sim_col.operator("seg.prev", icon="TRIA_LEFT")
        sim_col_2.operator("seg.next", icon = "TRIA_RIGHT")
