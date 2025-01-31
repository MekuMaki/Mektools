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
        print("Reading local manifest...")
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Local manifest: {data}")
            return data
    except Exception as e:
        print(f"Error loading local manifest: {e}")
        return None


def get_remote_manifest(branch):
    """Fetches the manifest.json from the GitHub repository."""
    url = f"{GITHUB_RAW_URL}{branch}/manifest.json"
    print(f"Fetching remote manifest from: {url}")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Remote manifest: {data}")
            return data
        else:
            print(f"Failed to fetch remote manifest. Status code: {response.status_code}")
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

    print(f"Comparing versions: Local {local_version}, Remote {remote_version}")
    print(f"Feature branch: {feature_name}, Local patch: {local_feature_patch}, Remote patch: {remote_feature_patch}")

    if feature_name in ["main", "dev"]:
        return tuple(remote_version) > tuple(local_version)
    else:
        return remote_feature_patch > local_feature_patch


def check_for_updates():
    """Checks if an update is available and shows a pop-up if needed."""
    print("Checking for updates...")
    local_manifest = get_local_manifest()
    if not local_manifest:
        print("Local manifest not found.")
        return

    branch = local_manifest.get("feature_name", "main")
    remote_manifest = get_remote_manifest(branch)
    if not remote_manifest:
        print("Remote manifest not found.")
        return

    if compare_versions(local_manifest, remote_manifest):
        print("Update available! Showing popup...")
        show_update_popup(branch)
    else:
        print("No update available.")


def show_update_popup(branch):
    """Schedules the popup to run in a UI-safe context."""
    def delayed_popup():
        def draw(self, context):
            self.layout.label(text="A new version of MekTools is available!")
            self.layout.operator("mektools.update_now", text="Download Update", icon='URL')
            self.layout.operator("mektools.dismiss_update", text="Dismiss", icon='CANCEL')
        
        bpy.context.window_manager.popup_menu(draw, title="Update Available", icon='INFO')
        return None  # Ensures timer doesn't repeat

    # Schedule popup on next UI update cycle
    bpy.app.timers.register(delayed_popup, first_interval=0.1)



class MekToolsUpdateNow(bpy.types.Operator):
    """Operator to open the update link."""
    bl_idname = "mektools.update_now"
    bl_label = "Update Now"
    
    def execute(self, context):
        branch = get_local_manifest().get("feature_name", "main")
        url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{branch}.zip"
        print(f"Opening update URL: {url}")
        bpy.ops.wm.url_open(url=url)
        return {'FINISHED'}


class MekToolsDismissUpdate(bpy.types.Operator):
    """Operator to dismiss the update notification."""
    bl_idname = "mektools.dismiss_update"
    bl_label = "Dismiss Update"
    
    def execute(self, context):
        print("Update dismissed.")
        return {'FINISHED'}


def register():
    print("Registering update check operators...")
    bpy.utils.register_class(MekToolsUpdateNow)
    bpy.utils.register_class(MekToolsDismissUpdate)
    bpy.app.timers.register(check_for_updates, first_interval=3)  # Runs after startup


def unregister():
    print("Unregistering update check operators...")
    bpy.utils.unregister_class(MekToolsUpdateNow)
    bpy.utils.unregister_class(MekToolsDismissUpdate)

