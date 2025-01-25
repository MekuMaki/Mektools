import bpy
from bpy.types import Panel, Operator

class VIEW3D_PT_GLBExport(Panel):
    bl_idname = "VIEW3D_PT_GLBExport"
    bl_label = "GLTF Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mektools"
    
    
    def draw(self, context):
        layout = self.layout
        layout.operator("export_action.glb", text="Animation Export").arg = "Exports the selected action as a GLB animation with custom settings"
        layout.operator("export_vfxobj.glb", text="VFX Model Export").arg = "Exports selected VFX model as GLB with optimized settings for VFX objects"



def register():
    bpy.utils.register_class(VIEW3D_PT_GLBExport)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_GLBExport)
