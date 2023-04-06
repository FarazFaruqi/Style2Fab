import bpy 
bpy.ops.preferences.addon_enable(module='plugin')
bpy.ops.wm.save_userpref()
bpy.ops.script.reload()