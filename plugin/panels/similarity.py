import bpy
from bpy.types import Panel
from bpy.props import EnumProperty

### Global Constants ###

class Similarity_PT_Panel(Panel):
    """
    AF() = a panel for SmartStyle3D
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Similarity"
    bl_category = "FA3DS"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout

        similarity_row = layout.row()
        similarity_col = similarity_row.column()
        similarity_col.operator("mesh.similarity", icon = "PLUGIN")

        assembly_enums = context.scene.assembly_enums
        if len(assembly_enums) == 2:
            mesh_row = layout.row()

            mesh_col_1 = mesh_row.column()
            mesh_col_2 = mesh_row.column()

            mesh_col_1.prop(assembly_enums[0], "model_enum")
            mesh_col_2.prop(assembly_enums[1], "model_enum")

            mesh_row = layout.row()

            mesh_col_1 = mesh_row.column()
            mesh_col_2 = mesh_row.column()
            
            found = 0
            selected_model_id, selected_other_id = None, None
            selected_i, selected_j = "0", "0"
            for model in context.scene.models:
                if f"{model.name.lower()}" == assembly_enums[0].model_enum:
                    mesh_col_1.prop(model, "segment_enum")
                    selected_i = model.segment_enum
                    selected_model_id = model.id
                    found += 1
                
                if f"{model.name.lower()}" == assembly_enums[1].model_enum:
                    mesh_col_2.prop(model, "segment_enum")
                    selected_j = model.segment_enum
                    selected_other_id = model.id
                    found += 1
                
                if found == 2: break

            if (selected_model_id is not None) and (selected_other_id is not None):
                for similarity in context.scene.similarity:
                    model_id, i = similarity.model_id, similarity.i
                    other_id, j = similarity.other_id, similarity.j
                    if model_id == selected_model_id and \
                    other_id == selected_other_id and \
                    f"{i}" == selected_i and f"{j}" == selected_j:
                        layout.label(text=f"Similarity: {similarity.sim:.3f}")
                        break

            layout.row().prop(context.scene, "t")
            sim_row = layout.row()
            sim_col = sim_row.column()
            sim_col_2 = sim_row.column()
            sim_col.operator("mesh.prev_sim", icon="TRIA_LEFT")
            sim_col_2.operator("mesh.next_sim", icon = "TRIA_RIGHT")

        # segment_col_1.label(text="segment 1")
        # segment_col_2.label(text="segment 2")
        # segment_col_1.prop(context.scene, "assembly_segment_1")
        # segment_col_2.prop(context.scene, "assembly_segment_2")

        