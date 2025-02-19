import bpy
from bpy.types import Panel
from ..addon_preferences import get_addon_preferences 
      
class VIEW3D_PT_PoseHelper(Panel):
    bl_idname = "VIEW3D_PT_PoseHelper"
    bl_label = "Pose Helper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mektools"
    
    bpy.types.Scene.orientation_mode = bpy.props.EnumProperty(
        name="Orientation Mode",
        description="Switch between different transformation orientations",
        items=[
            ('GLOBAL', "Global", "Use Global Orientation"),
            ('LOCAL', "Local", "Use Local Orientation"),
            ('NORMAL', "Normal", "Use Normal Orientation"),
            ('GIMBAL', "Gimbal", "Use Gimbal Orientation"),
            ('VIEW', "View", "Use View Orientation"),
            ('CURSOR', "Cursor", "Use Cursor Orientation"),
            ('PARENT', "Parent", "Use Parent Orientation"),
        ],
        default='GLOBAL',
        update=lambda self, context: setattr(
            bpy.context.scene.transform_orientation_slots[0], "type", self.orientation_mode
        )
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'
    
    def draw(self, context):
        self.prefs = get_addon_preferences()
        
        is_object_mode = context.object.mode == 'OBJECT'
        is_pose_mode = context.object.mode == 'POSE'
        
        layout = self.layout
        
        col = layout.column(align=False)
        col.label(text="Pose File")
        row = col.row()
        if self.prefs.ex_button_import_pose == 'ON':
            row.operator("pose.import", text="Import", icon="IMPORT")
        row.operator("pose.export", text="Export", icon="EXPORT")
        
        if self.prefs.general_transform_tools == 'ON':
            col = layout.column(align=False)
            col.label(text="Controls")
            row = col.row()
            row.scale_x = 1.1
            row.scale_y = 1.2
            row.alignment = 'CENTER'
            # Get the current tool
            active_tool = bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode).idname

            # Select Tool
            move_btn = row.operator("wm.tool_set_by_id", text="", icon="RESTRICT_SELECT_OFF", depress=(active_tool == "builtin.select_box"))
            move_btn.name = "builtin.select_box"
            
            row.separator(factor=1.0)
                        
            # Move Tool
            move_btn = row.operator("wm.tool_set_by_id", text="", icon="ORIENTATION_VIEW", depress=(active_tool == "builtin.move"))
            move_btn.name = "builtin.move"
            
            # Rotate Tool
            rotate_btn = row.operator("wm.tool_set_by_id", text="", icon="ORIENTATION_GIMBAL", depress=(active_tool == "builtin.rotate"))
            rotate_btn.name = "builtin.rotate"
            
            # Scale Tool
            scale_btn = row.operator("wm.tool_set_by_id", text="", icon="OBJECT_ORIGIN", depress=(active_tool == "builtin.scale"))
            scale_btn.name = "builtin.scale"
            
            # Orientation Mode
            row = col.row(align=True)
            row.label(text="Orientation:")
            row.prop(context.scene, "orientation_mode", text="")
            
            
        if self.prefs.general_pose_mode_toggle == "ON":
            col.separator(factor=1.5)
            
            row = layout.row(align=True)

            obj_mode_btn = row.operator("object.mode_set", text="Object Mode", depress=is_object_mode)
            obj_mode_btn.mode = 'OBJECT'

            pose_mode_btn = row.operator("object.mode_set", text="Pose Mode", depress=is_pose_mode)
            pose_mode_btn.mode = 'POSE'
            
        if is_pose_mode:
            col = layout.column(align=False)
            col.label(text="Reset Bones")
            row = col.row()
            row.operator("pose.reset", text="Pose", icon="OUTLINER_OB_ARMATURE")
            row.operator("pose.reset_selection", text="Selection", icon="BONE_DATA")
           

def register():
    bpy.utils.register_class(VIEW3D_PT_PoseHelper)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_PoseHelper)

    
    
    
    
    