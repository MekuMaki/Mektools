import bpy 

def register():
    bpy.types.Scene.import_with_meddle_shader = bpy.props.BoolProperty(
        name="Import with Meddle Shader",
        description="Applies the characters respective Meddle shader during import.",
        default=True
    )

def unregister():
    del bpy.types.Scene.import_with_meddle_shader