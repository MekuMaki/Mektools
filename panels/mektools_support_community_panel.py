import bpy 
import json
import os
from bpy.types import Panel

# Function to get version, feature name, and feature patch from the JSON file
def get_version_from_json():
    json_path = os.path.join(os.path.dirname(__file__), "..", "manifest.json")
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            version_list = data.get("version", ["Unknown"])
            feature_name = data.get("feature_name", "main")
            feature_patch = data.get("feature_patch", 0)
            
            # Extract only the last word from the feature name (strip any prefix)
            feature_name = feature_name.split("/")[-1] if "/" in feature_name else feature_name
            
            # Convert version list to string
            version = ".".join(map(str, version_list)) if isinstance(version_list, list) else str(version_list)
            
            # Append feature name if it's not "main"
            if feature_name.lower() != "main":
                version += f" ({feature_name}"
                
                # Append feature patch if it's not 0
                if feature_patch != 0:
                    version += f".{feature_patch}"
                version += ")"
            
            return version
    except Exception as e:
        print(f"Error reading version file: {e}")
        return "Unknown Version"

class VIEW3D_PT_SupportCommunity(Panel):
    bl_idname = "VIEW3D_PT_support_community"
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mektools'
    
    def draw_header(self, context):
        """Dynamically set the panel label using the version number, feature name, and feature patch."""
        self.layout.label(text=f"MekTools {get_version_from_json()}")

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.url_open", text="Support me on Patreon!", icon="URL").url = "https://www.patreon.com/MekuuMaki"
        layout.operator("wm.url_open", text="Support Shino on Patreon!", icon="URL").url = "https://www.patreon.com/ShinoMythmaker"
        layout.operator("wm.url_open", text="Join the Discord! (18+ only)", icon="URL").url = "https://www.discord.gg/98DqcKE"

def register():
    bpy.utils.register_class(VIEW3D_PT_SupportCommunity)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_SupportCommunity)
