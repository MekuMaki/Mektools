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

update_available = False  # Tracks if an update is available
update_installed = False  # Tracks if an update was successfully installed

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
    update_available = False  # Default to no update

    if not local or not remote:
        return  # If either manifest is missing, don't trigger an update

    # Extract version information
    local_version = local.get("version", [0, 0, 0])  # Defaults to [0, 0, 0]
    remote_version = remote.get("version", [0, 0, 0])

    # Convert version lists to tuples for comparison
    local_version_tuple = tuple(local_version)
    remote_version_tuple = tuple(remote_version)

    # Extract feature branch info
    local_feature = local.get("feature_name", "main")
    remote_feature = remote.get("feature_name", "main")

    local_feature_patch = local.get("feature_patch", 0)
    remote_feature_patch = remote.get("feature_patch", 0)

    # Compare versions
    if remote_version_tuple > local_version_tuple:
        update_available = True  # Major, minor, or patch update available

    # If versions are the same, compare feature patches (only for feature branches)
    elif remote_version_tuple == local_version_tuple:
        if local_feature == remote_feature and remote_feature_patch > local_feature_patch:
            update_available = True  # Feature patch update available

    # Debugging output
    print(f"Local version: {local_version} ({local_feature}.{local_feature_patch})")
    print(f"Remote version: {remote_version} ({remote_feature}.{remote_feature_patch})")
    print(f"Update available: {update_available}")

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
        global update_available, update_installed
        
        bpy.context.window.cursor_set('WAIT')

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

        # Step 3: Extract and replace the existing extension
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

        # Step 4: Mark update as installed and reset update_available
        update_installed = True
        update_available = False  # No more updates available

        self.report({'INFO'}, "Update installed! Please restart Blender to apply changes.")
        
        bpy.context.window.cursor_set('DEFAULT')
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
        
        layout.operator("wm.url_open", text="Socials", icon="HEART").url = "https://www.patreon.com/MekuuMaki"
        
        row = layout.row()
        row.operator("wm.url_open", text="Wiki", icon="HELP").url = "https://github.com/MekuMaki/MekTools/wiki"
        row.operator("wm.url_open", text="Issues", icon="BOOKMARKS").url = "https://github.com/MekuMaki/MekTools/issues"
        
        layout.separator()
        
        if update_available:
            layout.label(text="Update Available!", icon="ERROR")
            layout.operator("mektools.install_update", text="Install Update")

        # Show "Restart Blender" button only if an update was installed
        if update_installed:
            layout.label(text="Update installed, pls restart!", icon="FILE_REFRESH")
            layout.operator("mektools.restart_blender", text="Restart Blender", icon="FILE_REFRESH")

def register():
    bpy.utils.register_class(MEKTOOLS_OT_InstallUpdate)
    bpy.utils.register_class(MEKTOOLS_OT_RestartBlender)
    bpy.utils.register_class(VIEW3D_PT_SupportCommunity)
    bpy.app.timers.register(check_for_updates, first_interval=3)  # Auto-check after 3 seconds
    

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_InstallUpdate)
    bpy.utils.unregister_class(MEKTOOLS_OT_RestartBlender)
    bpy.utils.unregister_class(VIEW3D_PT_SupportCommunity)

