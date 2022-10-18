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
from .panel import FA3DS_PT_Panel
from .operators.segment import Segment_OT_Op
from .operators.stylize import Stylize_OT_Op
from .operators.select_segment import SelectSegment_OT_Op
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty
from .operators.show_mesh_info import ShowModelInfoFunction_OT_Op, ShowModelInfoForm_OT_Op

class Segments(bpy.types.PropertyGroup):
    i: IntProperty()
    label: StringProperty()
    faces: StringProperty()
    color: StringProperty()
    selected: BoolProperty(default = False)

class Model(bpy.types.PropertyGroup):
    name: StringProperty()
    show_form: BoolProperty(default = True)
    stylized: BoolProperty(default = False)
    segmented: BoolProperty(default = False)
    show_function: BoolProperty(default = True)
    segments: CollectionProperty(type = Segments)

classes = (Stylize_OT_Op, SelectSegment_OT_Op, Segment_OT_Op, ShowModelInfoForm_OT_Op, ShowModelInfoFunction_OT_Op, Segments, FA3DS_PT_Panel, Model)
props = {
    'prompt': StringProperty(
        name = "", 
        default = 'A vase made of wood'
    ),

    'models': CollectionProperty(
        type = Model
    )
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