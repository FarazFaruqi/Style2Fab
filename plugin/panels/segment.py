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
                
                for label in ["Function", "Form"]:
                    if not model.show_form and label == "Form": 
                        layout.operator(f"mesh.show_mesh_info_form", text=f"{label} Components", icon="TRIA_DOWN")
                        continue
                    if not model.show_function and label == "Function": 
                        layout.operator(f"mesh.show_mesh_info_function", text=f"{label} Components", icon="TRIA_DOWN")
                        continue
                    layout.operator(f"mesh.show_mesh_info_{label.lower()}", text=f"{label} Components", icon="TRIA_UP")

                    for i in range(len(model.segments)):
                        segment = model.segments[i]
                        if segment.label == label.lower():
                            segment_row = layout.row()
                            segment_col = segment_row.column()
                            segment_col.prop(segment, "selected", text=f"Part {i} - {segment.color}")
                layout.separator()
                
            layout.operator("mesh.select_segment", icon = "CHECKMARK")