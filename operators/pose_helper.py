import bpy
from bpy.types import Operator

class POSE_RESET_OT(Operator):
    """Reset Transform of every Bone in Armature"""
    bl_idname = "pose.reset"
    bl_label = "Reset Pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        armature = context.object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected.")
            return {'CANCELLED'}
        
        for bone in armature.pose.bones:
            bone.location = (0, 0, 0)
            bone.rotation_quaternion = (1, 0, 0, 0)
            bone.scale = (1, 1, 1)
        
        self.report({'INFO'}, "Pose Reset for all bones.")
        return {'FINISHED'}
    
class POSE_RESET_OT_Selection(Operator):
    """Reset Transform of selected Bones"""
    bl_idname = "pose.reset_selection"
    bl_label = "Reset Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        armature = context.object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected.")
            return {'CANCELLED'}
        
        selected_bones = [bone for bone in armature.pose.bones if bone.bone.select]
        if not selected_bones:
            self.report({'WARNING'}, "No bones selected.")
            return {'CANCELLED'}
        
        for bone in selected_bones:
            bone.location = (0, 0, 0)
            bone.rotation_quaternion = (1, 0, 0, 0)
            bone.scale = (1, 1, 1)
        
        self.report({'INFO'}, "Pose Reset for selected bones.")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(POSE_RESET_OT)
    bpy.utils.register_class(POSE_RESET_OT_Selection)

def unregister():
    bpy.utils.unregister_class(POSE_RESET_OT)
    bpy.utils.unregister_class(POSE_RESET_OT_Selection)