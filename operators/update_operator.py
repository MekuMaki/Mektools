import bpy
import requests
import json

# GitHub Repository Details
GITHUB_USER = "MekuMaki"
GITHUB_REPO = "MekTools"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/"

# Local manifest path
MANIFEST_PATH = bpy.utils.user_resource("SCRIPTS") + "/addons/MekTools/manifest.json"


def get_local_manifest():
    """Reads the local manifest.json file."""
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading local manifest: {e}")
        return None


def get_remote_manifest(branch):
    """Fetches the manifest.json from the GitHub repository."""
    url = f"{GITHUB_RAW_URL}{branch}/manifest.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching remote manifest: {e}")
    return None


def compare_versions(local, remote):
    """Compares version numbers and determines if an update is available."""
    local_version = local.get("version", [0, 0, 0])
    remote_version = remote.get("version", [0, 0, 0])
    local_feature_patch = local.get("feature_patch", 0)
    remote_feature_patch = remote.get("feature_patch", 0)
    feature_name = local.get("feature_name", "")

    if feature_name in ["main", "dev"]:
        return tuple(remote_version) > tuple(local_version)
    else:
        return remote_feature_patch > local_feature_patch


def check_for_updates():
    """Checks if an update is available and shows a pop-up if needed."""
    local_manifest = get_local_manifest()
    if not local_manifest:
        return

    branch = local_manifest.get("feature_name", "main")
    remote_manifest = get_remote_manifest(branch)
    if not remote_manifest:
        return

    if compare_versions(local_manifest, remote_manifest):
        show_update_popup(branch)


def show_update_popup(branch):
    """Displays a pop-up message with an update link."""
    def draw(self, context):
        self.layout.label(text="A new version of MekTools is available!")
        self.layout.operator("mektools.update_now", text="Download Update", icon='URL')
        self.layout.operator("mektools.dismiss_update", text="Dismiss", icon='CANCEL')
    
    bpy.context.window_manager.popup_menu(draw, title="Update Available", icon='INFO')


class MekToolsUpdateNow(bpy.types.Operator):
    """Operator to open the update link."""
    bl_idname = "mektools.update_now"
    bl_label = "Update Now"
    
    def execute(self, context):
        branch = get_local_manifest().get("feature_name", "main")
        url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{branch}.zip"
        bpy.ops.wm.url_open(url=url)
        return {'FINISHED'}


class MekToolsDismissUpdate(bpy.types.Operator):
    """Operator to dismiss the update notification."""
    bl_idname = "mektools.dismiss_update"
    bl_label = "Dismiss Update"
    
    def execute(self, context):
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MekToolsUpdateNow)
    bpy.utils.register_class(MekToolsDismissUpdate)
    bpy.app.timers.register(check_for_updates, first_interval=3)  # Runs after startup


def unregister():
    bpy.utils.unregister_class(MekToolsUpdateNow)
    bpy.utils.unregister_class(MekToolsDismissUpdate)
