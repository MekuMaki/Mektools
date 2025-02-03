import bpy
import json
import os

from .panels import (
    info_panel, 
    mektools_import_panel,
    pose_panel,
    glb_export_panel,
    
    
)
from .operators import (
    import_meddle_gltf, 
    import_textools_fbx, 
    export_pose, 
    import_pose,
    export_glb, 
    mekrig_operators, 
    append_shaders,
    lizzer_auto_shaders, 
    fixer_operators, 
    pose_helper,
)

from . import (
    addon_preferences,
)


bl_info = {
    "name": "MekTools",
    "author": "",
    "version": (1,3,6),
    "blender": (  "blender": [4, 2, 0],),
    "description": "A collection of tools for working with FFXIV models in Blender.",
    "category": "",
    "location": "View3D > Mektools Tab",
}

def register():
    # Register all panels
    info_panel.register()
    mektools_import_panel.register()
    pose_panel.register()
    glb_export_panel.register()
    
    # Register all operators
    import_meddle_gltf.register()
    import_textools_fbx.register()
    export_pose.register()
    import_pose.register()
    export_glb.register()
    mekrig_operators.register()
    append_shaders.register()
    lizzer_auto_shaders.register()
    fixer_operators.register()
    pose_helper.register()
    
    #register all preferences
    addon_preferences.register()

def unregister():
    # Unregister all panels
    info_panel.unregister()
    mektools_import_panel.unregister()
    pose_panel.unregister()
    glb_export_panel.unregister()
    
    # Unregister all operators
    import_meddle_gltf.unregister()
    import_textools_fbx.unregister()
    export_pose.unregister()
    import_pose.unregister()
    export_glb.unregister()
    mekrig_operators.unregister()
    append_shaders.unregister()
    lizzer_auto_shaders.unregister()
    fixer_operators.unregister()
    pose_helper.unregister()
   
    #unregister all preferences
    addon_preferences.unregister() 
    
    

if __name__ == "__main__":
    register()
    
