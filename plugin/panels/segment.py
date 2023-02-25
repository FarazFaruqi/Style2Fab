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
    bl_category = "FA3DS"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout
        seg_col = layout.column()
        seg_row = seg_col.row()
        seg_row.label(text="# segments:")
        seg_row.prop(context.scene, "num_segs")

        layout.operator("mesh.segment_mesh", icon = "PLUGIN")

        if len(context.scene.models) > 0:
            for model in context.scene.models:
                if not model.segmented: continue
                layout.label(text=f"{model.name.capitalize()}")
                
                for i in range(len(model.segments)):
                    segment = model.segments[i]

                    if segment.selected: draw_segment_cursor(layout, segment); break
                else: draw_segment_cursor(layout, model.segments[0])

                layout.operator("mesh.update_labels", text="Save", icon="CHECKMARK")
                layout.separator()
                
            # layout.operator("mesh.select_segment", icon = "CHECKMARK")

### Helper Functions ###
def draw_segment_cursor(layout, segment): 
    label_row = layout.row()
    form_col = label_row.column()
    func_col = label_row.column()
    form_col.prop(segment, "is_form", text=f"Form")
    func_col.prop(segment, "is_func", text=f"Function")

    seg_row = layout.row()
    seg_col = seg_row.column()
    seg_col_2 = seg_row.column()
    seg_col.operator("mesh.prev_segment", icon="TRIA_LEFT")
    seg_col_2.operator("mesh.next_segment", icon = "TRIA_RIGHT")