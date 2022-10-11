import bpy
from bpy.types import Panel
from bpy.props import BoolProperty

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
        
        layout.operator("mesh.segment_mesh", icon = "PLUGIN")

        if len(context.scene.segments) > 0:
            for label in ["Function", "Form"]:
                layout.label(text=f"{label} Components", icon="TRIA_DOWN")
                for i in range(len(context.scene.segments)):
                    segment = context.scene.segments[i]
                    if segment.label == label.lower():
                        segment_row = layout.row()
                        segment_col = segment_row.column()
                        segment_col.prop(segment, "selected", text=f"Part {i} - {segment.color}")

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
