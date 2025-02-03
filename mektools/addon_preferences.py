import bpy
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty

def get_addon_preferences():
    return bpy.context.preferences.addons[__package__].preferences

class MektoolsPreferences(AddonPreferences):
    bl_idname = __package__

    tabs: EnumProperty(
        name="Tabs",
        description="Select a preference tab",
        items=[
            ('GENERAL', "General", "General settings"),
            ('LEGACY', "Legacy Buttons", "Enable or disable legacy buttons"),
        ],
        default='GENERAL'
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

    # Legacy Buttons Section
    show_legacy_buttons: BoolProperty(
        name="Enable Legacy Buttons",
        description="Show options for deprecated or rarely used features",
        default=False
    )

    legacy_button_import_shaders: BoolProperty(
        name="Enable Legacy Import Shaders",
        description="Toggle this legacy button on or off",
        default=False
    )

    legacy_button_apply_shaders: BoolProperty(
        name="Enable Legacy Apply Shaders",
        description="Toggle this legacy button on or off",
        default=False
    )
    
    legacy_button_fix_backface_culling: BoolProperty(
        name="Enable Legacy Fix backface Culling",
        description="Toggle this legacy button on or off",
        default=False
    )
    
    legacy_button_clear_custom_split_normals: BoolProperty(
        name="Enable Legacy Clear Custom Split Normals",
        description="Toggle this legacy button on or off",
        default=False
    )
    
    legacy_button_clear_parents_keep_transform: BoolProperty(
        name="Enable Legacy Clear parents (Keep Transform)",
        description="Toggle this legacy button on or off",
        default=False
    )

    def draw(self, context):
        layout = self.layout

        # Tabs
        row = layout.row()
        row.prop(self, "tabs", expand=True)

        if self.tabs == 'GENERAL':
            box = layout.box()
            box.label(text="Default File Paths")
            box.prop(self, "default_meddle_import_path")
            box.prop(self, "default_textools_import_path")
            box.prop(self, "default_pose_import_path")
            box.prop(self, "default_pose_export_path")

        elif self.tabs == 'LEGACY':
            box = layout.box()
            box.label(text="Legacy Buttons")
            box.prop(self, "show_legacy_buttons")

            if self.show_legacy_buttons:
                legacy_box = box.box()
                legacy_box.label(text="Enable/Disable Legacy Buttons")
                legacy_box.prop(self, "legacy_button_import_shaders")
                legacy_box.prop(self, "legacy_button_apply_shaders")
                legacy_box.prop(self, "legacy_button_fix_backface_culling")
                legacy_box.prop(self, "legacy_button_clear_custom_split_normals")
                legacy_box.prop(self, "legacy_button_clear_parents_keep_transform")

def register():
    bpy.utils.register_class(MektoolsPreferences)

def unregister():
    bpy.utils.unregister_class(MektoolsPreferences)

