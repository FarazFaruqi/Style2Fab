import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class Segment_PT_Panel(Panel):
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
        # seg_col = layout.column()
        # seg_row = seg_col.row()
        # seg_row.label(text="no. segments:")
        # seg_row.prop(context.scene, "num_segs")

        layout.operator("mesh.segment", icon = "PLUGIN")

        if len(context.scene.models) > 0:
            for model in context.scene.models:
                if not model.segmented: continue
                layout.label(text=f"{model.name.capitalize()}")
                layout.label(text=f"No. Segments: {len(model.segments)}")
                
                # selected segment index
                j = 0
                for i in range(len(model.segments)):
                    segment = model.segments[i]

                    if segment.selected: j = i; break
                layout.label(text=f"Selected Segment: {j}")
                if j >= 0 and j < len(model.segments): _draw_segment_cursor(layout, model.segments[j])

                layout.operator("mesh.annotate", text="Save", icon="CHECKMARK")
            layout.operator("segment.select_func", icon = "PLUGIN")

### Helper Functions ###
def _draw_segment_cursor(layout, segment): 
    label_row = layout.row()
    form_col = label_row.column()
    func_col = label_row.column()
    form_col.prop(segment, "is_form", text=f"Form")
    func_col.prop(segment, "is_func", text=f"Function")

    seg_row = layout.row()
    seg_col = seg_row.column()
    seg_col_2 = seg_row.column()
    seg_col.operator("segment.prev", icon="TRIA_LEFT")
    seg_col_2.operator("segment.next", icon = "TRIA_RIGHT")