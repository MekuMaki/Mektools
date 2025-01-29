import bpy
import json
import os

from .panels import (
    mektools_support_community_panel, 
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


from .properties import (
    import_panel_properties,
)

from .preferences import (
    pose_preferences,
)


bl_info = {
    "name": "Mektools",
    "author": "Meku Maki, Shino Mythmaker",
    "version": (1,3,0),
    "blender": (4,2),
    "description": "Mektools Addon Structure",
    "category": "Import-Export",
    "location": "View3D > Mektools Tab",
}

def register():
    # Register all panels
    mektools_support_community_panel.register()
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
    

    #register all properties
    import_panel_properties.register()
    
    #register all preferences
    pose_preferences.register()

def unregister():
    # Unregister all panels
    mektools_support_community_panel.unregister()
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

    #unregister all properties
    import_panel_properties.unregister()   
    
    #unregister all preferences
    pose_preferences.unregister() 
    
    

if __name__ == "__main__":
    register()
    
