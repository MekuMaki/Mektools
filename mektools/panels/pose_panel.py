import bpy
from bpy.types import Panel
   
class VIEW3D_PT_PoseHelper(Panel):
    bl_idname = "VIEW3D_PT_PoseHelper"
    bl_label = "Pose Helper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mektools"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=False)
        col.label(text="Pose File")
        row = col.row()
        row.operator("pose.import", text="Import",icon="IMPORT")
        row.operator("pose.export", text="Export",icon = "EXPORT")
        
        col = layout.column(align=False)
        col.label(text="Reset Bones")
        row = col.row()
        row.operator("pose.reset", text="Pose",icon = "OUTLINER_OB_ARMATURE")
        row.operator("pose.reset_selection", text="Selection",icon = "BONE_DATA")
        

        

def register():
    bpy.utils.register_class(VIEW3D_PT_PoseHelper)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_PoseHelper)
    
    
    