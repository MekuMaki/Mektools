import bpy
from bpy.types import Operator
import os

# Define the path to the assets folder and shaders file
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "../assets")
SHADERS_FILE = os.path.join(ASSETS_PATH, "shaders.blend")

class MEKTOOLS_OT_AppendShaders(Operator):
    """Append all materials from shaders.blend"""
    bl_idname = "mektools.append_shaders"
    bl_label = "Append Shaders"
    bl_description = "Append Shaders from WOL Shaders by Skulblaka"  # Set the tooltip here

    def execute(self, context):
        if not os.path.exists(SHADERS_FILE):
            self.report({'ERROR'}, f"File not found: {SHADERS_FILE}")
            return {'CANCELLED'}

        # Load materials from shaders.blend
        with bpy.data.libraries.load(SHADERS_FILE, link=False) as (data_from, data_to):
            data_to.materials = [mat for mat in data_from.materials if mat not in bpy.data.materials]

        self.report({'INFO'}, f"Appended {len(data_to.materials)} materials from shaders.blend")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MEKTOOLS_OT_AppendShaders)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_AppendShaders)
