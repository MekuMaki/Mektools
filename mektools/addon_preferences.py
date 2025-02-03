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

    # Legacy Buttons with Proper Toggle Layout
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

            def draw_toggle(label, prop_name):
                row = box.row()
                row.label(text=label)
                row.prop(self, prop_name, expand=True)

            row = box.row()
            row.label(text="Import")
            draw_toggle("Import Shaders", "legacy_button_import_shaders")
            draw_toggle("Apply Shaders", "legacy_button_apply_shaders")
            
            row = box.row()
            row.label(text="Fixer")
            draw_toggle("Fix Backface Culling", "legacy_button_fix_backface_culling")
            draw_toggle("Clear Custom Split Normals", "legacy_button_clear_custom_split_normals")
            draw_toggle("Clear Parents (Keep Transform)", "legacy_button_clear_parents_keep_transform")

def register():
    bpy.utils.register_class(MektoolsPreferences)

def unregister():
    bpy.utils.unregister_class(MektoolsPreferences)

    bpy.utils.unregister_class(MektoolsPreferences)


