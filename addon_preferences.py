import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, EnumProperty

def get_addon_preferences():
    return bpy.context.preferences.addons[__package__].preferences

class MektoolsPreferences(AddonPreferences):
    bl_idname = __package__

    tabs: EnumProperty(
        name="Tabs",
        description="Select a preference tab",
        items=[
            ('GENERAL', "General", "General settings"),
            ('PATHS', "Paths", "Set default paths for various functions"),
            ('EXPERIMENTAL', "Experimental", "Enabel or disable experimental buttrons"),
            ('LEGACY', "Legacy Buttons", "Enable or disable legacy buttons"),
        ],
        default='GENERAL'
    )

 
    general_transform_tools: EnumProperty(
        name="Transform Tools",
        description="Enables/Disables Transform helper buttons for users that are unfamiliar with blender controls",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 
    
    general_pose_mode_toggle: EnumProperty(
        name="PoseMode Toggle",
        description="Enables/Disables Pose Mode toggle buttons for users that are unfamiliar with blender controls",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 

    # Default File Paths
    default_meddle_import_path: StringProperty(
        name="Meddle GLTF Import",
        subtype='DIR_PATH',
        description="Select the default directory for importing Meddle GLTF files"
    ) 

    default_textools_import_path: StringProperty(
        name="Textools FBX Import",
        subtype='DIR_PATH',
        description="Select the default directory for importing Textools FBX files"
    ) 

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

    # Experimental Buttons          
    ex_button_import_pose: EnumProperty(
        name="Import Pose",
        description="Enables/Disables Pose Import function",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 
    
    ex_button_spline_tail: EnumProperty(
        name="Spline Tail",
        description="Enables/Disables import option to generate a spline IK around the tail.",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 
    
    ex_button_spline_gear: EnumProperty(
        name="Spline Gear",
        description="Enables/Disables import option to generate a spline IK around the the gear.",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 
    
    # Legacy Buttons
    legacy_button_import_shaders: EnumProperty(
        name="Import Shaders",
        description="Toggle this legacy button on or off",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 

    legacy_button_apply_shaders: EnumProperty(
        name="Apply Shaders",
        description="Toggle this legacy button on or off",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 

    legacy_button_fix_backface_culling: EnumProperty(
        name="Fix Backface Culling",
        description="Toggle this legacy button on or off",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 

    legacy_button_clear_custom_split_normals: EnumProperty(
        name="Clear Custom Split Normals",
        description="Toggle this legacy button on or off",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 

    legacy_button_clear_parents_keep_transform: EnumProperty(
        name="Clear Parents (Keep Transform)",
        description="Toggle this legacy button on or off",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 
    
    legacy_button_import_rigs: EnumProperty(
        name="Import Rigs",
        description="Toggle this legacy button on or off",
        items=[('OFF', "Disable", ""), ('ON', "Enable", "")],
        default='OFF'
    ) 

    def draw(self, context):
        def draw_toggle(label, prop_name):
                row = box.row()
                row.label(text=label)
                row.prop(self, prop_name, expand=True)
        
        layout = self.layout

        # Tabs
        row = layout.row()
        row.prop(self, "tabs", expand=True)
        
        if self.tabs == 'GENERAL':
            box = layout.box()
            box.label(text="General Settings")
             
            box = layout.box()
            box.label(text="Pose Helper")
            draw_toggle("PoseMode Toggle", "general_pose_mode_toggle")
            draw_toggle("Transform Tools", "general_transform_tools")
            
        elif self.tabs == 'PATHS':
            box = layout.box()
            box.label(text="Default File Paths")
            box.prop(self, "default_meddle_import_path")
            box.prop(self, "default_textools_import_path")
            box.prop(self, "default_pose_import_path")
            box.prop(self, "default_pose_export_path")
            
        elif self.tabs == 'EXPERIMENTAL':
            box = layout.box()
            box.label(text="Experimental Features")
            
            box.label(text="These features are in development and may not function as expected.")
            box.label(text="Use them at your own discretion, and feel free to provide feedback.")

            box = layout.box()
            box.label(text="Meddle Import")
            draw_toggle("Import with Spline Tail", "ex_button_spline_tail")
            #draw_toggle("Import with Spline Gear", "ex_button_spline_gear")
            
            box = layout.box()
            box.label(text="Pose Helper")
            draw_toggle("Import Pose", "ex_button_import_pose")

        elif self.tabs == 'LEGACY':
            box = layout.box()
            box.label(text="Legacy Buttons")
            
            box.label(text="These are buttons or functions that we are no longer actively supporting.")
            box.label(text="However if you miss them you can bring the back right here.")
        
            box = layout.box()
            box.label(text="Import")
            draw_toggle("Import Shaders", "legacy_button_import_shaders")
            draw_toggle("Apply Shaders", "legacy_button_apply_shaders")
            
            box = layout.box()
            box.label(text="Fixer")
            draw_toggle("Fix Backface Culling", "legacy_button_fix_backface_culling")
            draw_toggle("Clear Custom Split Normals", "legacy_button_clear_custom_split_normals")
            draw_toggle("Clear Parents (Keep Transform)", "legacy_button_clear_parents_keep_transform")
            
            box = layout.box()
            box.label(text="Rigs")
            draw_toggle("Import Rigs", "legacy_button_import_rigs")
            

def register():
    bpy.utils.register_class(MektoolsPreferences)

def unregister():
    bpy.utils.unregister_class(MektoolsPreferences)


