import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

### Global Constants ###

class FA3DS_PT_Panel(Panel):
    """
    AF() = a panel for SmartStyle3D
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Smart Style 3D"
    bl_category = "SmartStyle3D"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout
        
        # layout.label(text="Mesh")
        # mesh_col = layout.column()
        # mesh_row = mesh_col.row()
        # mesh_row.prop(context.scene, "selected_mesh")
        # mesh_col.operator("object.upload_mesh", icon = "ADD")

        # layout.separator()

        # layout.label(text="Segmentation")
        layout.label(text="Number of segments")
        seg_col = layout.column()
        seg_row = seg_col.row()
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
        layout.separator()
        # layout.label(text="Stylization")

        layout.label(text="Prompt")
        prompt_col = layout.column()
        prompt_row = prompt_col.row()
        prompt_row.prop(context.scene, "prompt")

        stylize_row = layout.row()
        stylize_col = stylize_row.column()
        stylize_col.operator("mesh.stylize_mesh", icon = "PLUGIN")
