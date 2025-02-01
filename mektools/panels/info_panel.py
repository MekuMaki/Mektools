import bpy
import requests
import json
import os
import tempfile
import shutil
import zipfile
import sys
import subprocess
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
class MEKTOOLS_OT_RestartBlender(bpy.types.Operator):
    """Restart Blender"""
    bl_idname = "mektools.restart_blender"
    bl_label = "Restart Blender"

    def execute(self, context):
        self.report({'INFO'}, "Restarting Blender...")

        # Get Blender executable path
        blender_exe = sys.argv[0]  # This should point to Blender's executable

        # Ensure the executable exists before proceeding
        if not os.path.exists(blender_exe):
            self.report({'ERROR'}, "Could not determine Blender executable path.")
            return {'CANCELLED'}

        # Restart Blender
        try:
            subprocess.Popen([blender_exe])  # Launch a new Blender process
            bpy.ops.wm.quit_blender()  # Close current instance
        except Exception as e:
            self.report({'ERROR'}, f"Failed to restart Blender: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}
    
class MEKTOOLS_OT_InstallUpdate(bpy.types.Operator):
    """Download and install the latest version of MekTools"""
    bl_idname = "mektools.install_update"
    bl_label = "Install Update"

    def execute(self, context):
        # Step 1: Get the current branch name
        local_manifest = get_local_manifest()
        if not local_manifest:
            self.report({'ERROR'}, "Failed to read local manifest.")
            return {'CANCELLED'}
        
        branch = local_manifest.get("feature_name", "main")
        download_url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{branch}.zip"

        # Step 2: Download the update ZIP file
        self.report({'INFO'}, "Downloading update...")
        try:
            response = requests.get(download_url, stream=True)
            if response.status_code != 200:
                self.report({'ERROR'}, "Failed to download update.")
                return {'CANCELLED'}
            
            # Save the file to a temporary location
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "update.zip")

            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        except Exception as e:
            self.report({'ERROR'}, f"Download failed: {e}")
            return {'CANCELLED'}

        # Step 3: Extract and correctly move the files
        self.report({'INFO'}, "Installing update...")

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                extracted_folder = os.path.join(temp_dir, "mektools_extracted")
                zip_ref.extractall(extracted_folder)

                # Locate the actual "mektools" folder inside the extracted directory
                extracted_main_folder = os.path.join(extracted_folder, os.listdir(extracted_folder)[0])  # This is "MekTools-main"
                extracted_mektools_folder = os.path.join(extracted_main_folder, "mektools")  # This is the actual extension

                # Ensure the target extension folder exists
                if not os.path.exists(MEKTOOLS_FOLDER):
                    os.makedirs(MEKTOOLS_FOLDER)

                # Remove the old version
                shutil.rmtree(MEKTOOLS_FOLDER, ignore_errors=True)

                # Move the inner "mektools" folder to the correct location
                shutil.move(extracted_mektools_folder, MEKTOOLS_FOLDER)

        except Exception as e:
            self.report({'ERROR'}, f"Installation failed: {e}")
            return {'CANCELLED'}

        # Step 4: Force Blender to recognize the updated extension
        
        global update_available
        update_available = False  # Reset the update flag

        self.report({'INFO'}, "Update installed! Please restart Blender to apply changes.")

        return {'FINISHED'}

class VIEW3D_PT_SupportCommunity(bpy.types.Panel):
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

        # Add Restart Blender Button
        layout.operator("mektools.restart_blender", text="Restart Blender", icon="FILE_REFRESH")

def register():
    bpy.utils.register_class(MEKTOOLS_OT_InstallUpdate)
    bpy.utils.register_class(VIEW3D_PT_SupportCommunity)
    bpy.app.timers.register(check_for_updates, first_interval=3)  # Auto-check after 3 seconds
    

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_InstallUpdate)
    bpy.utils.unregister_class(VIEW3D_PT_SupportCommunity)

