bl_info = {
    "name" : "Style2Fab",
    "author" : "Ahmed Katary",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Object"
}

import bpy 
from .operators.segment import Seg_OT_Op
from .operators.style import Style_OT_Op
from .operators.sim import Sim_OT_Op
from .operators.select_segment import Next_OT_Op, Prev_OT_Op, Func_OT_Op

from .panels.sim import Similar_PT_Panel
from .panels.style import Something_PT_Panel
from .panels.segment import Seg_PT_Panel
from .panels.select import Select_PT_Panel
from .panels.process import Process_PT_Panel

### Custom Properties ###
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty, EnumProperty, FloatProperty

classes = (
    Sim_OT_Op,
    Seg_OT_Op,
    Next_OT_Op, 
    Prev_OT_Op, 
    Func_OT_Op,
    Style_OT_Op,

    #Select_PT_Panel,
    #Seg_PT_Panel,
    #Something_PT_Panel,
    #Similar_PT_Panel,
    Process_PT_Panel,
)

props = {
    'prompt': StringProperty(
        name = "", 
        default = 'A vase made of wood'
    ),
    
    'codedModels': EnumProperty(
        name = "", 
        items = [
            ("vase", "vase", ""),
            ("cat", "cat", ""),
            ("planter", "planter", ""),
        ],
    ),

    'model_1': EnumProperty(
        name = "", 
        items = [
            ("pot", "pot", ""),
        ],
    ),

    'model_2': EnumProperty(
        name = "", 
        items = [
            ("reservoir", "reservoir", ""),
        ],
    ),

    'is_form': BoolProperty(default = False),
    'is_func': BoolProperty(default = True),
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