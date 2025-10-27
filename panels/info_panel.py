import bpy
from ..addon_preferences import get_addon_preferences 

# GitHub Repository Details
GITHUB_USER = "MekuMaki"
GITHUB_REPO = "MekTools"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/"

class VIEW3D_PT_SupportCommunity(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_support_community"
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mektools'
    
    def draw_header(self, context):
        self.layout.label(text="Mektools")

    def draw(self, context):
        layout = self.layout
        
        layout.operator("wm.url_open", text="Support & Links", icon="HEART").url = "https://mektools.carrd.co/"
        
        row = layout.row()
        row.operator("wm.url_open", text="Wiki", icon="HELP").url = "https://github.com/MekuMaki/MekTools/wiki"
        row.operator("wm.url_open", text="Issues", icon="BOOKMARKS").url = "https://github.com/MekuMaki/MekTools/issues"
        
        layout.separator()
    

def register():
    prefs = get_addon_preferences()
    bpy.utils.register_class(VIEW3D_PT_SupportCommunity) 
    

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_SupportCommunity)

