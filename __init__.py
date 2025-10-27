from .custom_icons import register_custom_icons, unregister_custom_icons

from . import (
    addon_preferences,
)

from .panels import (
    info_panel, 
    mektools_import_panel,
    pose_panel,
    glb_export_panel,
    opp_pt,
    rig_panel
        
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
    opp_ot,
)


def register():
    #Register Icons 
    register_custom_icons()
    
    #Register all preferences
    addon_preferences.register()
    
    # Register all operators types
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
    opp_ot.register()
   
    # Register all panel types
    info_panel.register()
    mektools_import_panel.register()
    pose_panel.register()
    glb_export_panel.register()
    opp_pt.register()
    rig_panel.register()

def unregister(): 
    # Unregister all panel types
    info_panel.unregister()
    mektools_import_panel.unregister()
    pose_panel.unregister()
    glb_export_panel.unregister()
    opp_pt.unregister()
    rig_panel.unregister()
    
    # Unregister all operator types
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
    opp_ot.unregister()
   
    #unregister all preferences
    addon_preferences.unregister() 
    
    # Unregister Icons 
    unregister_custom_icons()
    
    

if __name__ == "__main__":
    register()
    
