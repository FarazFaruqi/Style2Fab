bl_info = {
    "name" : "fa3ds",
    "author" : "Ahmed Katary",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Object"
}

import bpy 
from .panels.edit import Edit_PT_Panel
from .panels.style import Style_PT_Panel
from .panels.segment import Segment_PT_Panel
from .panels.fetch import MeshSelection_PT_Panel
from .panels.assembly import Assemble_PT_Panel

from .operators.edit import Edit_OT_Op
from .operators.delete import Delete_OT_Op
from .operators.segment import Segment_OT_Op
from .operators.stylize import Stylize_OT_Op
from .operators.annotate import Annotate_OT_Op
from .operators.assembly import Assemble_OT_Op
from .operators.select_mesh import Prev_OT_Op, Next_OT_Op
from .operators.select_segment import PrevSeg_OT_Op, NextSeg_OT_Op, SelectFunc_OT_Op
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty, EnumProperty, FloatProperty

def get_models(self, context):
    models = []
    seen = set()
    for model in context.scene.models:
        if model.name.lower() not in seen:
            seen.add(model.name.lower())
            models.append((f"{model.name.lower()}", f"{model.name.lower()}", ""))
    return models

def get_segments(self, context):
    segments = [(f"{segment.i}", f"{segment.i}", "") for segment in self.segments]
    return segments

### Custom Properties ###
class Segments(bpy.types.PropertyGroup):
    i: IntProperty()
    label: StringProperty()
    faces: StringProperty()
    color: StringProperty()
    face_matrix: StringProperty()
    vertex_matrix: StringProperty()
    is_form: BoolProperty(default = True)
    is_func: BoolProperty(default = False)
    selected: BoolProperty(default = False)

class Model(bpy.types.PropertyGroup):
    id: StringProperty()
    name: StringProperty()
    show_form: BoolProperty(default = True)
    stylized: BoolProperty(default = False)
    segmented: BoolProperty(default = False)
    show_function: BoolProperty(default = True)
    segments: CollectionProperty(type = Segments)
    segment_enum: EnumProperty(name = "", items = get_segments)

class DynamicEnum(bpy.types.PropertyGroup):
    model_enum: EnumProperty(name = "", items = get_models)

class Simalrity(bpy.types.PropertyGroup):
    j: IntProperty() # model_segment_id
    i: IntProperty() # other_segment_id
    model_id: StringProperty()
    other_id: StringProperty()
    sim: FloatProperty(name="similarity", precision=2)

classes = (
    Edit_OT_Op, 
    Prev_OT_Op,
    Next_OT_Op,
    Delete_OT_Op,
    Segment_OT_Op,
    Stylize_OT_Op, 
    PrevSeg_OT_Op,
    NextSeg_OT_Op,
    Annotate_OT_Op,
    Assemble_OT_Op,
    SelectFunc_OT_Op,

    Segments, 
    # SegmentEnum,
    Model,
    DynamicEnum,
    Simalrity,

    Segment_PT_Panel,
    Assemble_PT_Panel,
    Style_PT_Panel,
    Edit_PT_Panel, 
    MeshSelection_PT_Panel,
)

props = {
    'prompt': StringProperty(
        name = "", 
        default = 'A vase made of wood'
    ),

    'num_segs': IntProperty(
        name = "", 
        default = 5
    ),

    'i': IntProperty(
        name = "", 
        default = 0
    ),

    'num_meshes': IntProperty(
        name = "", 
        default = 0
    ),

    'mesh_dir': StringProperty(
        name = "", 
        default = "/home/ubuntu/fa3ds/backend/results/study_models"
    ),

    'face_count': IntProperty(
        name = "", 
        default = 0
    ),

    'vertex_count': IntProperty(
        name = "", 
        default = 0
    ),

    'models': CollectionProperty(
        type = Model
    ),

    'mode': EnumProperty(
        name = "mode", 
        items = [
            ("remesh", "remesh", ""),
            ("face collapse", "face collapse", ""),
            ("edge collapse", "edge collapse", ""),
        ],
    ),

    'assembly_enums': CollectionProperty(
        type = DynamicEnum
    ),

    'similarity': CollectionProperty(
        type = Simalrity
    ),
}

def register():
    """ """
    for class_ in classes: bpy.utils.register_class(class_)
    for prop_name, prop_value in props.items(): setattr(bpy.types.Scene, prop_name, prop_value)

def unregister():
    """ """
    for class_ in classes: bpy.utils.unregister_class(class_)

if __name__ == "__main__":
    register()