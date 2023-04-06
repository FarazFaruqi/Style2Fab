import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class Seg_PT_Panel(Panel):
    """
    AF() = a panel for Segmentation
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Segment"
    bl_category = "Style2Fab"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout

        layout.operator("mesh.seg", icon = "PLUGIN")

        layout.label(text=f"{context.scene.codedModels.capitalize()}")
        layout.label(text=f"No. Segments: 3")

        label_row = layout.row()
        form_col = label_row.column()
        func_col = label_row.column()
        form_col.prop(context.scene, "is_form", text=f"Aesthetic")
        func_col.prop(context.scene, "is_func", text=f"Functional")

        seg_row = layout.row()
        seg_col = seg_row.column()
        seg_col_2 = seg_row.column()
        seg_col.operator("seg.prev", icon="TRIA_LEFT")
        seg_col_2.operator("seg.next", icon = "TRIA_RIGHT")

        layout.operator("seg.select_func", icon = "PLUGIN")