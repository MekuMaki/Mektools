import bpy
from bpy.types import Panel
   
class VIEW3D_PT_ImportExportPose(Panel):
    bl_idname = "VIEW3D_PT_ImportExportPose"
    bl_label = "Pose Import and Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mektools"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        
        
        # Import button
        layout.operator("import_pose.file", text="Import Pose File",icon="IMPORT")
        
        # Export button
        layout.operator("export_pose.file", text="Export to Pose File",icon = "EXPORT")
        

        

def register():
    bpy.utils.register_class(VIEW3D_PT_ImportExportPose)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_ImportExportPose)
    
    
    