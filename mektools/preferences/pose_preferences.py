import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty
import os


class PosePreferences(PropertyGroup):
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


def draw_preferences(self, context, layout):
    """ Function to draw the preferences in the Extensions panel """
    layout.label(text="Default File Paths")
    layout.prop(context.preferences.extensions['MekTools'].preferences, "default_pose_import_path")
    layout.prop(context.preferences.extensions['MekTools'].preferences, "default_pose_export_path")


def register():
    bpy.utils.register_class(PosePreferences)
    bpy.types.Preferences.extensions.register("MekTools", PosePreferences, draw=draw_preferences)


def unregister():
    bpy.utils.unregister_class(PosePreferences)
    bpy.types.Preferences.extensions.unregister("MekTools")
