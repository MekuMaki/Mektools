import bpy
import requests
import json
import os
import shutil
from bpy.types import Panel, Operator

# GitHub Repository Details
GITHUB_USER = "MekuMaki"
GITHUB_REPO = "MekTools"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/"

# Local manifest path
EXTENSIONS_PATH = bpy.utils.user_resource('EXTENSIONS', path="user_default")
MEKTOOLS_FOLDER = os.path.join(EXTENSIONS_PATH, "mektools")
update_available = False  # Global flag for update status

def get_local_manifest():
    manifest_path = os.path.join(MEKTOOLS_FOLDER, "manifest.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading local manifest: {e}")
        return None

def get_remote_manifest(branch):
    url = f"{GITHUB_RAW_URL}{branch}/mektools/manifest.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching remote manifest: {e}")
    return None

def format_version_string():
    manifest = get_local_manifest()
    if not manifest:
        return "MekTools Unknown Version"
    
    version_list = manifest.get("version", ["Unknown"])
    feature_name = manifest.get("feature_name", "main")
    feature_patch = manifest.get("feature_patch", 0)
    
    feature_name = feature_name.split("/")[-1] if "/" in feature_name else feature_name
    version = ".".join(map(str, version_list)) if isinstance(version_list, list) else str(version_list)
    
    if feature_name.lower() != "main":
        version += f" ({feature_name}"
        if feature_patch != 0 and feature_name.lower() != "dev":
            version += f".{feature_patch}"
        version += ")"
    
    return f"MekTools {version}"

def compare_versions(local, remote):
    global update_available
    update_available = True  # Force update for debugging

def check_for_updates():
    local_manifest = get_local_manifest()
    if not local_manifest:
        return
    
    branch = local_manifest.get("feature_name", "main")
    remote_manifest = get_remote_manifest(branch)
    if not remote_manifest:
        return
    
    compare_versions(local_manifest, remote_manifest)

    # Ensure the UI updates correctly
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':  # Only refresh VIEW_3D where the panel is located
                area.tag_redraw()

class MEKTOOLS_OT_InstallUpdate(Operator):
    bl_idname = "mektools.install_update"
    bl_label = "Install Update"
    
    def execute(self, context):
        branch = get_local_manifest().get("feature_name", "main")
        url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{branch}.zip"
        bpy.ops.wm.url_open(url=url)
        return {'FINISHED'}

class VIEW3D_PT_SupportCommunity(Panel):
    bl_idname = "VIEW3D_PT_support_community"
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mektools'
    
    def draw_header(self, context):
        self.layout.label(text=format_version_string())

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("wm.url_open", text="Support", icon="HEART").url = "https://www.patreon.com/MekuuMaki"
        row.operator("wm.url_open", text="Wiki").url = "https://github.com/MekuMaki/MekTools/wiki"
        row.operator("wm.url_open", text="Issues").url = "https://github.com/MekuMaki/MekTools/issues"
        
        layout.separator()
        
        if update_available:
            layout.label(text="Update Available!", icon="ERROR")
            layout.operator("mektools.install_update", text="Install Update")

def register():
    bpy.utils.register_class(MEKTOOLS_OT_InstallUpdate)
    bpy.utils.register_class(VIEW3D_PT_SupportCommunity)
    bpy.app.timers.register(check_for_updates, first_interval=3)  # Auto-check after 3 seconds
    

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_InstallUpdate)
    bpy.utils.unregister_class(VIEW3D_PT_SupportCommunity)

