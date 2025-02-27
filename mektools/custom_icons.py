import os
import bpy
import bpy.utils.previews

preview_collections = {}

def register_custom_icons():
    """Loads custom icons into Blender's preview system."""
    custom_icons = bpy.utils.previews.new()

    # Get the addon folder path and locate the icons folder
    icons_dir = os.path.join(os.path.dirname(__file__), "assets/icons")

    # Load icons from files
    custom_icons.load("BONE_DATA_OFF", os.path.join(icons_dir, "bone_data_off.svg"), 'IMAGE')
    
    preview_collections["main"] = custom_icons

def unregister_custom_icons():
    """Unregisters custom icons to prevent memory leaks."""
    for custom_icons in preview_collections.values():
        bpy.utils.previews.remove(custom_icons)
    preview_collections.clear()

