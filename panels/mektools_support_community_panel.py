import bpy
from bpy.types import Panel

class VIEW3D_PT_SupportCommunity(Panel):
    bl_label = "MekTools 1.2.10" 
    bl_idname = "VIEW3D_PT_support_community"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mektools'

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.url_open", text="Support me on Patreon!", icon="URL").url = "https://www.patreon.com/MekuuMaki"
        layout.operator("wm.url_open", text="Support Shino on Patreon!", icon="URL").url = "https://www.patreon.com/ShinoMythmaker"
        layout.operator("wm.url_open", text="Join the Discord! (18+ only)", icon="URL").url = "https://www.discord.gg/98DqcKE"

def register():
    bpy.utils.register_class(VIEW3D_PT_SupportCommunity)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_SupportCommunity)
