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
from .panels.mesh_selection import MeshSelection_PT_Panel

from .operators.edit import Edit_OT_Op
from .operators.delete import Delete_OT_Op
from .operators.next_mesh import Next_OT_Op
from .operators.prev_mesh import Prev_OT_Op
from .operators.segment import Segment_OT_Op
from .operators.stylize import Stylize_OT_Op
from .operators.prev_segment import PrevSeg_OT_Op
from .operators.next_segment import NextSeg_OT_Op
from .operators.update_labels import UpdateLabels_OT_Op
from .operators.show_mesh_info import ShowModelInfoFunction_OT_Op, ShowModelInfoForm_OT_Op
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty, EnumProperty

class Segments(bpy.types.PropertyGroup):
    i: IntProperty()
    label: StringProperty()
    faces: StringProperty()
    color: StringProperty()
    is_form: BoolProperty(default = True)
    is_func: BoolProperty(default = False)
    selected: BoolProperty(default = False)

class Model(bpy.types.PropertyGroup):
    name: StringProperty()
    show_form: BoolProperty(default = True)
    stylized: BoolProperty(default = False)
    segmented: BoolProperty(default = False)
    show_function: BoolProperty(default = True)
    segments: CollectionProperty(type = Segments)

classes = (
    Edit_OT_Op, 
    Prev_OT_Op,
    Next_OT_Op,
    Delete_OT_Op,
    Segment_OT_Op,
    Stylize_OT_Op, 
    PrevSeg_OT_Op,
    NextSeg_OT_Op,
    UpdateLabels_OT_Op,
    SelectSegment_OT_Op, 
    ShowModelInfoForm_OT_Op, 
    ShowModelInfoFunction_OT_Op, 

    Segments, 
    Model, 

    Segment_PT_Panel,
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

    'mesh_dir': StringProperty(
        name = "", 
        default = "/home/ubuntu/fa3ds/backend/segment/segment_utils/models"
    ),

    'models': CollectionProperty(
        type = Model
    ),

    'mode': EnumProperty(
        name = "mode", 
        items = [
            ("remesh", "remesh", ""),
            ("collapse", "collapse", ""),
        ],
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