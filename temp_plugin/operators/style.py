import bpy

### Constants ###

class Style_OT_Op(bpy.types.Operator):
    """ Stylize a mesh """

    bl_idname = "mesh.style"
    bl_label = "Stylize"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        return True

    def execute(self, context):
        """Executes the segmentation"""
        return {'FINISHED'}