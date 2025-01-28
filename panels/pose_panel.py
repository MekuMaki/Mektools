import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import BoolProperty, PointerProperty

BONE_GROUPS = ["Hair", "Face", "HandL", "HandR", "Tail", "Gear", "Body"]

# Property Group to store selection states for each bone group
class BoneGroupProperties(PropertyGroup):
    Hair: BoolProperty(name="Hair", default=False)
    Face: BoolProperty(name="Face", default=False)
    HandL: BoolProperty(name="HandL", default=False)
    HandR: BoolProperty(name="HandR", default=False)
    Tail: BoolProperty(name="Tail", default=False)
    Gear: BoolProperty(name="Gear", default=False)
    Body: BoolProperty(name="Body", default=False)

   
    
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
        bone_group_props = context.scene.bone_group_props
        
        
        # Import button
        layout.operator("import_pose.file", text="Import Pose File",icon="IMPORT")
        
        # Export button
        layout.operator("export_pose.file", text="Export to Pose File",icon = "EXPORT")
        
        layout.row().separator()

        # Create toggles for each bone group
        layout.prop(bone_group_props, "Hair", toggle=True, text="Hair")
        layout.prop(bone_group_props, "Face", toggle=True, text="Face")
        
        row = layout.row()
        row.prop(bone_group_props, "HandL", toggle=True, text="HandL")
        row.prop(bone_group_props, "HandR", toggle=True, text="HandR")
        
        layout.prop(bone_group_props, "Tail", toggle=True, text="Tail")
        layout.prop(bone_group_props, "Gear", toggle=True, text="Gear")
        layout.prop(bone_group_props, "Body", toggle=True, text="Body")
        

        

def register():
    bpy.utils.register_class(BoneGroupProperties)
    bpy.utils.register_class(VIEW3D_PT_ImportExportPose)
    bpy.types.Scene.bone_group_props = PointerProperty(type=BoneGroupProperties)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_ImportExportPose)
    bpy.utils.unregister_class(BoneGroupProperties)
    del bpy.types.Scene.bone_group_props
    
    
    