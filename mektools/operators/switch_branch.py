import bpy
import requests
import json
import os
import shutil
from bpy.types import Panel, Operator, AddonPreferences
from bpy.props import EnumProperty

# GitHub Repository Details
GITHUB_USER = "MekuMaki"
GITHUB_REPO = "MekTools"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/"
GITHUB_API_BRANCHES = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/branches"

# Local manifest path
ADDONS_PATH = bpy.utils.user_resource("SCRIPTS") + "/addons/"
MEKTOOLS_FOLDER = os.path.join(ADDONS_PATH, "MekTools")
update_available = False  # Global flag for update status

def get_available_branches():
    """Fetches available branches from GitHub."""
    try:
        response = requests.get(GITHUB_API_BRANCHES, timeout=5)
        if response.status_code == 200:
            branches = response.json()
            return [(branch["name"], branch["name"], "") for branch in branches]
    except Exception as e:
        print(f"Error fetching branches: {e}")
    return [("main", "main", ""), ("dev", "dev", "")]  # Default options

class MekToolsPreferences(AddonPreferences):
    bl_idname = "Mektools"
    
    branch: EnumProperty(
        name="Branch",
        description="Select the branch to use",
        items=[("main", "main", ""), ("dev", "dev", "")],   #get_available_branches(),
        default="main",
    )
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="MekTools Update Settings")
        layout.prop(self, "branch")
        layout.operator("mektools.switch_branch", text="Switch to Selected Branch")

class MEKTOOLS_OT_SwitchBranch(Operator):
    bl_idname = "mektools.switch_branch"
    bl_label = "Switch Branch"
    
    def execute(self, context):
        prefs = bpy.context.preferences.addons[__name__].preferences
        selected_branch = prefs.branch
        print(f"Switching to branch: {selected_branch}")
        
        url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{selected_branch}.zip"
        zip_path = os.path.join(ADDONS_PATH, f"{selected_branch}.zip")
        
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(zip_path, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                
                shutil.unpack_archive(zip_path, ADDONS_PATH)
                extracted_folder = os.path.join(ADDONS_PATH, f"{GITHUB_REPO}-{selected_branch}")
                if os.path.exists(extracted_folder):
                    shutil.rmtree(MEKTOOLS_FOLDER, ignore_errors=True)
                    shutil.move(extracted_folder, MEKTOOLS_FOLDER)
                os.remove(zip_path)
                print("Successfully switched branches.")
            else:
                print("Failed to download branch.")
        except Exception as e:
            print(f"Error switching branches: {e}")
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MekToolsPreferences)
    bpy.utils.register_class(MEKTOOLS_OT_SwitchBranch)

def unregister():
    bpy.utils.unregister_class(MekToolsPreferences)
    bpy.utils.unregister_class(MEKTOOLS_OT_SwitchBranch)