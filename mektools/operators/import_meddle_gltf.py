import bpy
from bpy.types import Operator
import os
import importlib.util
from math import radians
from bpy.props import BoolProperty
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

def import_meddle_shader(self, imported_meshes):
    for mesh in imported_meshes:
        mesh.select_set(True)   
        
    character_directory = os.path.dirname(self.filepath)
    meddle_cache_directory = os.path.join(character_directory, "cache","")

    try:
        bpy.ops.meddle.use_shaders_selected_objects('EXEC_DEFAULT', directory=meddle_cache_directory)

    except AttributeError:
        self.report({'ERROR'}, "Meddle shaders couldn't be imported. Try restarting Blender and try again.")

    except Exception as e:
        self.report({'ERROR'}, f"Failed to append Meddle shaders: {e}")
        
def remove_pole_parents(armature):
    """Removes the parent from IK pole bones in the given armature."""
    if armature and armature.type == 'ARMATURE':
        # Switch to Edit Mode (Needed to modify parent relationships)
        bpy.ops.object.mode_set(mode='EDIT')

        bones_to_unparent = ["IK_Arm_Pole.R", "IK_Arm_Pole.L", "IK_Leg_Pole.R", "IK_Leg_Pole.L"]

        for bone_name in bones_to_unparent:
            if bone_name in armature.data.edit_bones:
                bone = armature.data.edit_bones[bone_name]
                bone.parent = None  # Unparent the bone

        # Return to Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')
        print("Removed parent from IK pole bones.")
    else:
        print("No armature selected or incorrect object type.")   

def filter_bones(mesh_filter_string, objects_to_filter, bone_names_to_skip = []):
    """Returns a set of bone names that influence meshes whose name contains the mesh_filter_string.    

    :param mesh_filter_string: substring to look for in mesh object names. Only meshes 
        containing this string in their name will be processed. Matching is case-sensitive.
    :type mesh_filter_string: str
    :param objects_to_filter: list of objects to check for bone influences
    :type objects_to_filter: list
    :param bone_names_to_skip: optional list of bone names to exclude from results. 
        Defaults to empty list if not provided.
    :type bone_names_to_skip: list, optional
    :return: set of influential bone names after filtering
    :rtype: set
    """

    previous_object_mode_state = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    filtered_objects = [obj for obj in objects_to_filter if mesh_filter_string in obj.name]
    influential_bones = set()
    for obj in filtered_objects:

        for vgroup in obj.vertex_groups:
            if vgroup.name in bone_names_to_skip:  
                continue
            if any(vgroup.index in [g.group for g in v.groups if g.weight > 0] for v in obj.data.vertices):
                influential_bones.add(vgroup.name)

    bpy.ops.object.mode_set(mode=previous_object_mode_state)
    return influential_bones


def append_mekrig(self,objects_imported, string_to_grab_racial_code="iri"):
    """Appends the mekrig to the current scene and cleans it up.

    :param objects_imported: list of objects to check for racial code
    :type objects_imported: list
    :param string_to_grab_racial_code: string to grab the racial code from
    :type string_to_grab_racial_code: str, optional
    :return: mekrig collection, mekrig armature
    :rtype: collection, armature
    """

    all_collections_before_mekrig = set(bpy.data.collections)

    racial_code_object = next(
        (obj for obj in objects_imported if string_to_grab_racial_code in obj.name or any(string_to_grab_racial_code in mat.name for mat in obj.material_slots)),
        None
    )

    for code in racial_code_to_operator:
        if code in racial_code_object.name:
            operator_id = racial_code_to_operator[code]
            eval(f"bpy.ops.{operator_id}()")
            break

    all_collections_after_mekrig = set(bpy.data.collections)
    substracted_collections = all_collections_after_mekrig - all_collections_before_mekrig
    if not substracted_collections:
        self.report({'ERROR'}, "No collection found in the imported objects.")
        return ({'CANCELLED'})

    mekrig_collection = None
    for collection in substracted_collections:
        #mekrig's top level collection is usually named {racial_code}_male or {racial_code}_female
        if "male" in collection.name or "female" in collection.name:
            mekrig_collection = collection
            break
    if not mekrig_collection:
        self.report({'ERROR'}, "No collection found in the imported objects.")
        return ({'CANCELLED'})

    return mekrig_collection

def apply_mekrig_armature(self, original_gltf_armature, mekrig_armature, objects_imported, influential_bones):
    """Merges the mekrig armature with the original gltf armature and returns the combined armature.

    :param original_gltf_armature: Original gltf armature
    :type original_gltf_armature: bpy.types.Object
    :param mekrig_armature: Mekrig armature
    :type mekrig_armature: bpy.types.Object
    :param objects_imported: List of imported objects
    :type objects_imported: list
    :return: Combined armature
    :rtype: bpy.types.Object
    """

    #base mekrig is called "n_root"
    mekrig_armature = next(
        (obj for obj in objects_imported 
         if obj.type == 'ARMATURE' 
         and "n_root" in obj.name),
        None
    )
    if not mekrig_armature:
        self.report({'ERROR'}, "No n_root armature found in the imported objects.")
        return ({'CANCELLED'})

    #we need to change the name rather than leaving it because the next character will be expecting the armature to be "n_root"
    #but it will be "n_root.001" and the above code will fail
    mekrig_armature.name = "Armature"

    
    bpy.ops.object.mode_set(mode='OBJECT')

    # We need to deselect everything before parenting the imported meshes to n_root
    # Just to make sure we dont have an object selected that we dont want to parent
    bpy.ops.object.select_all(action='DESELECT')

    for mesh in objects_imported:
        if mesh.type == 'MESH':
            mesh.select_set(True)   

    mekrig_armature.select_set(True)
    bpy.context.view_layer.objects.active = mekrig_armature
    bpy.ops.object.parent_set(type='OBJECT')

    # set armature modifier to mekrig_armature
    for mesh in objects_imported:
        if mesh.type == 'MESH':
            for mod in mesh.modifiers:
                if mod.type == 'ARMATURE': 
                    mod.object = mekrig_armature  

    #deselect all to ensure only the armatures are selected
    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.view_layer.objects.active = mekrig_armature
    original_gltf_armature.select_set(True)
    mekrig_armature.select_set(True)
    bpy.ops.object.join()    

    #ima be real idk why we rotate the bones here but we do
    bpy.ops.object.mode_set(mode='EDIT')
    mek_kao_bone = mekrig_armature.data.edit_bones.get("mek kao")
    for bone in mekrig_armature.data.edit_bones:
        if bone.name in influential_bones:
            bone.parent = mek_kao_bone
            bone.roll = radians(90)

    bpy.ops.object.mode_set(mode='OBJECT')

    return mekrig_armature

def mergeMeshes(self, candidate_meshes, common_mesh_string):
    skin_meshes = [obj for obj in candidate_meshes if common_mesh_string in obj.name]
    
    # We select the first found mesh as the active object, so we can join all the other meshes to it
    bpy.context.view_layer.objects.active = skin_meshes[0]

    for mesh in skin_meshes:
        mesh.select_set(True)

    # And we merge 'em
    bpy.ops.object.join()   


    # Lastly we deselect everything
    bpy.ops.object.select_all(action='DESELECT')

def find_armature_in_objects(objects_imported):
    for obj in objects_imported:
        if obj.type == 'ARMATURE':
            return obj

    #im either crazy or return cancelled doesn't fucking work it just skips the error lmao
    return None

def rebuild_objects_imported(objects_before_import):
    #we create a list of objects that were i mported by substracting the
    #objects before the import from the objects after the import
    #and the difference (substraction) between the two is the objects that were imported
    #substracting sets is basic boolean math, btw
    objects_imported = set(bpy.data.objects) - objects_before_import
    return objects_imported

def cleanup_imported_gltf_armature(original_gltf_armature, bone_names_to_delete, objects_imported, influential_bones):
    state_before_cleanup = bpy.context.object.mode
    bpy.context.view_layer.objects.active = original_gltf_armature
    bpy.ops.object.mode_set(mode='EDIT')

    # Remove bones from bone_names.py
    for bone_name in bone_names_to_delete:
        if bone_name in original_gltf_armature.data.edit_bones:
            original_gltf_armature.data.edit_bones.remove(original_gltf_armature.data.edit_bones[bone_name])



    bpy.ops.object.mode_set(mode='EDIT')
    for bone in original_gltf_armature.data.edit_bones:
        if bone.name not in influential_bones:
            original_gltf_armature.data.edit_bones.remove(bone)


    bpy.ops.object.mode_set(mode=state_before_cleanup)

    # Switch to Pose Mode for hair bone adjustments
    bpy.ops.object.mode_set(mode='POSE')
    print("objects_imported: ", objects_imported)
    cs_hair = next((obj for obj in objects_imported if  "cs.hair" in obj.name), None)
    for bone_name in influential_bones:
        pose_bone = original_gltf_armature.pose.bones.get(bone_name)
        print("Searching for bone: ", bone_name)
        if pose_bone:
            print("Found bone: ", pose_bone.name)
            pose_bone.custom_shape = cs_hair
            print("Setting custom shape to: ", cs_hair.name)
            pose_bone.color.palette = 'THEME01'  # Theme 1 Red

    bpy.ops.object.mode_set(mode='OBJECT')

    return original_gltf_armature

def clear_parents_keep_transform(objects_to_clear):
    for obj in objects_to_clear:
        obj.select_set(True)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        obj.select_set(False)

class MEKTOOLS_OT_ImportGLTFFromMeddle(Operator):
    """Import GLTF from Meddle and perform cleanup tasks"""
    bl_idname = "mektools.import_meddle_gltf"
    bl_label = "Import GLTF from Meddle"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default='*.gltf', options={'HIDDEN'})
    
    import_with_shaders_setting: BoolProperty(name="Import with Meddle Shaders", description="Tries to also import all shaders from meddle shader cache", default=True)
    remove_parent_on_poles: BoolProperty(name="Remove Parents from Pole-Targets", description="Removes the Parent from Pole-Targets", default=False)
    
    def invoke(self, context, event):
        prefs = get_addon_preferences()
        if prefs.default_meddle_import_path:
            self.filepath = prefs.default_meddle_import_path
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout

        layout.label(text="Import Settings")
      
        layout.prop(self, "import_with_shaders_setting", toggle=False)
        layout.prop(self, "remove_parent_on_poles", toggle=False)

    def execute(self, context):  
        bpy.context.window.cursor_set('WAIT')      

        #we keep a list (Set) of all objects before the import 
        objects_before_import = set(bpy.data.objects)

        # Import the selected GLTF file and capture the imported objects
        bpy.ops.import_scene.gltf(filepath=self.filepath)
        
        #we set aside the imported meshes to use later (bottom of class) to avoid having to rebuild the list of imported objects
        #though realistically we could just change it to objects_imported for consistency
        imported_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        # the gltf imports icospheres to use rather than bones, but those are ugly so we dont need them.
        # if we  dont delete them they just stay in the scene (even after importing mekrig) so we delete them
        icosphere = bpy.data.objects.get("Icosphere")
        if icosphere:
            bpy.data.objects.remove(icosphere)

        objects_imported = rebuild_objects_imported(objects_before_import)

        clear_parents_keep_transform(objects_imported)

        # Delete the "glTF_not_exported" collection if it exists
        collection_to_delete = bpy.data.collections.get("glTF_not_exported")
        if collection_to_delete:
            bpy.data.collections.remove(collection_to_delete)

        # Load the list of bone names to delete
        bone_names_to_delete = set(load_bone_names())  # Convert to a set for efficient lookups

        objects_imported = rebuild_objects_imported(objects_before_import)

        # Reference the armature of the imported objects
        original_gltf_armature = find_armature_in_objects(objects_imported)
        if not original_gltf_armature:
            self.report({'ERROR'}, "No armature found in the imported objects.")
            return {'CANCELLED'}
        #we append the mekrig first (even though we might not use it yet) because we need the import shapes for the gltf armature 
        #before merging it together and shit
        mekrig_collection = append_mekrig(self, objects_imported)
        if not mekrig_collection:
            self.report({'ERROR'}, "No armature collection found in the imported objects.")
            return {'CANCELLED'}     
        
        #we rebuild objects_imported since we added the mekrig 
        #if we dont rebuild and we iterate over objects_imported we will get a rna_error cause the objects wont exist anymore
        objects_imported = rebuild_objects_imported(objects_before_import)

        # we get the influential bones for the hir meshes
        # since those are the bones that influence the hair mesh, and we want to keep those and delete the rest
        # the mekrig doesn't contain hair bones (thank god it doesnt) so we use the gltf-imported armature's and append those to the mekrig
        influential_bones = filter_bones("hir", objects_imported, bone_names_to_delete)

        
        original_gltf_armature = cleanup_imported_gltf_armature(original_gltf_armature, bone_names_to_delete, objects_imported, influential_bones)
    

        mekrig_armature = apply_mekrig_armature(self, original_gltf_armature, mekrig_collection, objects_imported, influential_bones)

        #rebuild the list of objects imported since the mekrig got joined the original gltf armature
        objects_imported = rebuild_objects_imported(objects_before_import)
        
        if self.remove_parent_on_poles:
            remove_pole_parents(mekrig_armature)

        if self.import_with_shaders_setting:
            import_meddle_shader(self, imported_meshes)
        else:
            bpy.ops.mektools.append_shaders()
            bpy.ops.material.material_fixer_auto()

        for obj in imported_meshes:
            # Remove from all existing collections first if you want EXCLUSIVE membership
            for collection in obj.users_collection:
                collection.objects.unlink(obj)
            
            # Add to the target collection
            mekrig_collection.objects.link(obj)

        mergeMeshes(self, imported_meshes, "skin")

        # Lastly we deselect everything
        bpy.ops.object.select_all(action='DESELECT')

        self.report({'INFO'}, "GLTF imported and processed successfully.")
        bpy.context.window.cursor_set('DEFAULT')
        bpy.ops.ed.undo_push()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MEKTOOLS_OT_ImportGLTFFromMeddle)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportGLTFFromMeddle)