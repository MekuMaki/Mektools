import bpy
from bpy.types import Operator
import os
import importlib.util
from math import radians
from ..addon_preferences import get_addon_preferences 


# Load the bone names from bone_names.py in the data folder
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data")
BONE_NAMES_FILE = os.path.join(DATA_PATH, "bone_names.py")

# Define the racial code mapping to operator IDs in `mekrig_operators.py`
racial_code_to_operator = {
    'c0101': 'mektools.import_mekrig_midlander_male',
    'c0201': 'mektools.import_mekrig_midlander_female',
    'c0301': 'mektools.import_mekrig_highlander_male',
    'c0401': 'mektools.import_mekrig_highlander_female',
    'c0501': 'mektools.import_mekrig_elezen_male',
    'c0601': 'mektools.import_mekrig_elezen_female',
    'c0701': 'mektools.import_mekrig_miqote_male',
    'c0801': 'mektools.import_mekrig_miqote_female',
    'c0901': 'mektools.import_mekrig_roegadyn_male',
    'c1001': 'mektools.import_mekrig_roegadyn_female',
    'c1101': 'mektools.import_mekrig_lalafell_both',
    'c1201': 'mektools.import_mekrig_lalafell_both',
    'c1301': 'mektools.import_mekrig_aura_male',
    'c1401': 'mektools.import_mekrig_aura_female',
    'c1501': 'mektools.import_mekrig_hrothgar_male',
    'c1601': 'mektools.import_mekrig_hrothgar_female',
    'c1701': 'mektools.import_mekrig_viera_male',
    'c1801': 'mektools.import_mekrig_viera_female',
}

# Function to load bone names from bone_names.py
def load_bone_names():
    spec = importlib.util.spec_from_file_location("bone_names", BONE_NAMES_FILE)
    bone_names = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bone_names)
    return bone_names.bone_names  # This assumes bone_names.py defines a list named `bone_names`

class MEKTOOLS_OT_ImportGLTFFromMeddle(Operator):
    """Import GLTF from Meddle and perform cleanup tasks"""
    bl_idname = "mektools.import_meddle_gltf"
    bl_label = "Import GLTF from Meddle"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default='*.gltf', options={'HIDDEN'})

    def execute(self, context):  
        bpy.context.window.cursor_set('WAIT')      
        # Import the selected GLTF file and capture the imported objects
        bpy.ops.import_scene.gltf(filepath=self.filepath)
        
        # Capture only the newly imported mesh objects
        imported_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        # Step 1: Perform all cleanup tasks
        icosphere = bpy.data.objects.get("Icosphere")
        if icosphere:
            bpy.data.objects.remove(icosphere)

        # Clear parent for all objects and keep transform
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        # Delete the "glTF_not_exported" collection if it exists
        collection_to_delete = bpy.data.collections.get("glTF_not_exported")
        if collection_to_delete:
            bpy.data.collections.remove(collection_to_delete)

        # Load the list of bone names to delete
        bone_names_to_delete = set(load_bone_names())  # Convert to a set for efficient lookups

        # Reference the "Armature" object
        armature = bpy.data.objects.get("Armature")
        if not armature:
            self.report({'ERROR'}, "No armature found with the name 'Armature'.")
            return {'CANCELLED'}

        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')

        # Remove bones from bone_names.py
        for bone_name in bone_names_to_delete:
            if bone_name in armature.data.edit_bones:
                armature.data.edit_bones.remove(armature.data.edit_bones[bone_name])

        # Return to Object Mode temporarily
        bpy.ops.object.mode_set(mode='OBJECT')

        # Step 2: Filter influential bones for "hir" objects
        hir_objects = [obj for obj in bpy.data.objects if "hir" in obj.name]
        influential_bones = set()
        for obj in hir_objects:
            for vgroup in obj.vertex_groups:
                if vgroup.name in bone_names_to_delete:  # Skip bones listed in bone_names.py
                    continue
                if any(vgroup.index in [g.group for g in v.groups if g.weight > 0] for v in obj.data.vertices):
                    influential_bones.add(vgroup.name)

        bpy.ops.object.mode_set(mode='EDIT')
        for bone in armature.data.edit_bones:
            if bone.name not in influential_bones:
                armature.data.edit_bones.remove(bone)

        # Return to Object Mode after all bone operations
        bpy.ops.object.mode_set(mode='OBJECT')

        # Step 3: Append the correct Mekrig based on "iri" object
        iri_object = next(
            (obj for obj in bpy.data.objects if "iri" in obj.name or any("iri" in mat.name for mat in obj.material_slots)),
            None
        )

        for code in racial_code_to_operator:
            if code in iri_object.name:
                operator_id = racial_code_to_operator[code]
                eval(f"bpy.ops.{operator_id}()")
                break

        # Step 4: Join Armature with Mekrig and parent hair bones to "mek kao"
        n_root_armature = bpy.data.objects.get("n_root")
        bpy.context.view_layer.objects.active = n_root_armature
        armature.select_set(True)
        n_root_armature.select_set(True)
        bpy.ops.object.join()

        bpy.ops.object.mode_set(mode='EDIT')
        mek_kao_bone = n_root_armature.data.edit_bones.get("mek kao")
        for bone in n_root_armature.data.edit_bones:
            if bone.name in influential_bones:
                bone.parent = mek_kao_bone
                bone.roll = radians(90)

        # Switch to Pose Mode for hair bone adjustments
        bpy.ops.object.mode_set(mode='POSE')
        cs_hair = bpy.data.objects.get("cs.hair")
        for bone_name in influential_bones:
            pose_bone = n_root_armature.pose.bones.get(bone_name)
            if pose_bone:
                pose_bone.custom_shape = cs_hair
                pose_bone.color.palette = 'THEME01'  # Theme 1 Red

        bpy.ops.object.mode_set(mode='OBJECT')

        # We need to deselect everything before parenting the imported meshes to n_root
        # Just to make sure we dont have an object selected that we dont want to parent
        bpy.ops.object.select_all(action='DESELECT')

        # Step 5: Parent the items of imported_meshes items objects to "n_root"
        for mesh in imported_meshes:
            mesh.select_set(True)   

        n_root_armature.select_set(True)
        bpy.context.view_layer.objects.active = n_root_armature
        bpy.ops.object.parent_set(type='OBJECT')

        # Step 6: Update Armature Modifiers for imported meshes
        for obj in imported_meshes:
            for mod in obj.modifiers:
                if mod.type == 'ARMATURE':  # Check if it is an Armature modifier
                    mod.object = bpy.data.objects["n_root"]  # Set n_root as the target

        # Step 7: Fix/Append Shaders
        # If the user wants to append meddle shaders we append those, otherwise we just fix the materials
        if context.scene.import_with_meddle_shader:
            # Since the code above selects everything after import, we need to deselect everything before appending the shaders
            # Else Meddle might attempt to add a shader to the Default Cube or any other already existing meshes and will crash
            for mesh in imported_meshes:
                mesh.select_set(True)   

            # Get the character directory from the filepath
            # Since filepath points to the .gltf file, we need to go the directory where the gltf is found, not get the gltf itself
            character_directory = os.path.dirname(self.filepath)

            # The extra "" is added at the end because without it it would resolve to /character_directory/cache, which makes Meddle complain.
            # So with the extra "" it turns into /character_directory/cache/
            meddle_cache_directory = os.path.join(character_directory, "cache","")

            try:
                # We call the Meddle shader importer which will handle all the material assignments for us
                bpy.ops.meddle.use_shaders_selected_objects('EXEC_DEFAULT', directory=meddle_cache_directory)

            except AttributeError:
                self.report({'ERROR'}, "Meddle shaders couldn't be imported. Try restarting Blender and try again.")

            except Exception as e:
                self.report({'ERROR'}, f"Failed to append Meddle shaders: {e}")

        else:
            bpy.ops.mektools.append_shaders()
            bpy.ops.material.material_fixer_auto()


        # Step 8: Cleanup
        # We merge all meshes whose name contain "skin", as we would usually just do this manually. So why not automate that aswell lmao?
        skin_meshes = [obj for obj in imported_meshes if "skin" in obj.name]
        
        # We select the first found mesh as the active object, so we can join all the other meshes to it
        bpy.context.view_layer.objects.active = skin_meshes[0]

        for mesh in skin_meshes:
            mesh.select_set(True)

        # And we merge 'em
        bpy.ops.object.join()

        # Lastly we deselect everything
        bpy.ops.object.select_all(action='DESELECT')

        self.report({'INFO'}, "GLTF imported and processed successfully.")
        bpy.context.window.cursor_set('DEFAULT')
        bpy.ops.ed.undo_push()
        return {'FINISHED'}

    def invoke(self, context, event):
        prefs = get_addon_preferences()
        if prefs.default_meddle_import_path:
            self.filepath = prefs.default_meddle_import_path
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(MEKTOOLS_OT_ImportGLTFFromMeddle)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportGLTFFromMeddle)
