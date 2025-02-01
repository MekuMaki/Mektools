import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty

class PosePreferences(AddonPreferences):
    bl_idname = "Mektools" 

    default_pose_export_path: StringProperty(
        name="Pose Export",
        subtype='DIR_PATH',
        description="Select the default directory for saving pose files"
    )
    
    default_pose_import_path: StringProperty(
        name="Pose Import",
        subtype='DIR_PATH',
        description="Select the default directory for importing pose files"
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Default File Paths")
        layout.prop(self, "default_pose_import_path")
        layout.prop(self, "default_pose_export_path")
        

def register():
    bpy.utils.register_class(PosePreferences)

def unregister():
    bpy.utils.unregister_class(PosePreferences)