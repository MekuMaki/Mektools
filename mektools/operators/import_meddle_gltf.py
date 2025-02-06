import bpy
from bpy.types import Operator
import os
import importlib.util
from math import radians
from bpy.props import BoolProperty
from collections import defaultdict, namedtuple
import re
from ..addon_preferences import get_addon_preferences 


# Load the bone names from bone_names.py in the data folder
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data")
BONE_NAMES_FILE = os.path.join(DATA_PATH, "bone_names.py")

Stripped_Armature_Data = namedtuple("Stripped_Armature_Data", ["armature", "original_parents"])

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

def load_bone_names():
    spec = importlib.util.spec_from_file_location("bone_names", BONE_NAMES_FILE)
    bone_names = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bone_names)
    return bone_names.bone_names  # This assumes bone_names.py defines a list named `bone_names`

def import_meddle_shader(self, imported_objects):
    for obj in imported_objects:
        try:
            if obj and obj.type == "MESH": 
                obj.select_set(True)
        except ReferenceError:
            print(f"Skipping deleted object: {obj}")  
        
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

def append_mekrig(racial_code):
    """Appends the correct Mekrig depending on Racial Code and returns the armature and its collection."""

    scene_collections_before = set(bpy.data.collections)

    operator_id = racial_code_to_operator[racial_code]
    eval(f"bpy.ops.{operator_id}()")

    scene_collections_after = set(bpy.data.collections)

    new_collections = scene_collections_after - scene_collections_before
    
    imported_armature = None

    for collection in new_collections:
        for obj in collection.objects:
            if obj.type == "ARMATURE":  
                imported_armature = obj
                break     
        if imported_armature:
            break

    return imported_armature

def merge_armatures(armature_a, armature_b):
    """Merges armature B into armature A and updates only relevant objects that were using armature B.Returns the final merged armature (A)."""
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action='DESELECT')

    collection_a = next((col for col in bpy.data.collections if armature_a.name in col.objects), None)
    collection_b = next((col for col in bpy.data.collections if armature_b.name in col.objects), None)

    stripped_armature_data = remove_duplicate_bones(armature_a, armature_b)
    armature_b = stripped_armature_data.armature  

    objects_with_b = []
    for obj in bpy.context.scene.objects: 
        if obj.type == "MESH": 
            for mod in obj.modifiers:
                if mod.type == "ARMATURE" and mod.object == armature_b:
                    objects_with_b.append((obj, mod))

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = armature_a
    armature_a.select_set(True)
    armature_b.select_set(True)
    bpy.ops.object.join() 

    for obj, mod in objects_with_b:
        mod.object = armature_a  

    bpy.ops.object.mode_set(mode="OBJECT")

    restore_bone_parents(armature_a, stripped_armature_data.original_parents)

    if collection_a and collection_b and collection_a != collection_b:
        bpy.context.scene.collection.children.unlink(collection_a)
        collection_b.children.link(collection_a)

    return armature_a    

def restore_bone_parents(armature, original_parents):
    """Restores lost parent relationships in an armature after modifications."""
    bpy.ops.object.mode_set(mode="EDIT") 

    for bone_name, parent_name in original_parents.items():
        if bone_name in armature.data.edit_bones and parent_name in armature.data.edit_bones:
            armature.data.edit_bones[bone_name].parent = armature.data.edit_bones[parent_name]

    bpy.ops.object.mode_set(mode="OBJECT") 
                      
def merge_by_material(objects):
    """Merges objects that share the same material and returns the updated list of objects."""
    material_mesh_groups = defaultdict(list)

    for obj in objects:
        try:
            if obj.type == "MESH" and obj.data.materials:
                material_name = obj.data.materials[0].name
                material_mesh_groups[material_name].append(obj)
        except ReferenceError:
            print(f"Skipping deleted object: {obj}")

    new_objects = set()  

    for material, meshes in material_mesh_groups.items():
        if len(meshes) < 2:
            new_objects.update(meshes)  
            continue
        print(f"[Mektools] Merging {len(meshes)} meshes with material: {material}")
        bpy.ops.object.select_all(action='DESELECT')
        for mesh in meshes:
            mesh.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.join()
        merged_object = bpy.context.view_layer.objects.active
        new_objects.add(merged_object)

        bpy.ops.object.select_all(action='DESELECT')
        
    return list(new_objects)

def find_armature_in_objects(objects):
    """Finds the first armature in the objects imported."""
    for obj in objects:
        try:
            if obj.type == 'ARMATURE':
                return obj 
        except ReferenceError:
            print(f"Skipping deleted object: {obj}")
       
    return None

def get_bones_by_name(armature, name):
    """Returns a list of bone names that contain the nameStr in their name."""
    if armature and armature.type == "ARMATURE":
        return [bone for bone in armature.data.bones if name in bone.name]
    return []

def remove_duplicate_bones(armature_a, armature_b):
    """Removes bones from Armature A if they also exist in Armature B.Stores all parent relationships before making changes."""
    
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.objects.active = armature_b
    bpy.ops.object.mode_set(mode="EDIT")

    reference_bones = {bone.name for bone in armature_a.data.bones}

    original_parents = {}
    for bone in armature_b.data.edit_bones:
        if bone.parent:
            original_parents[bone.name] = bone.parent.name  

    for bone in armature_b.data.edit_bones[:]:  
        if bone.name in reference_bones:
            if bone.name in original_parents:
                del original_parents[bone.name]  
            armature_b.data.edit_bones.remove(bone)

    bpy.ops.object.mode_set(mode="OBJECT")
    
    return Stripped_Armature_Data(armature_b, original_parents)  

def clear_parents_keep_transform(objects_to_clear):
    """Clears the parent of the objects and keeps the transform."""
    for obj in objects_to_clear:
        try:
            obj.select_set(True)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            obj.select_set(False)
        except ReferenceError:
            print(f"Skipping deleted object: {obj}")

def link_objects_to_collection(objects, collection):
    """Links objects to a collection."""
    for obj in objects:
        try:
            for user_collection in obj.users_collection:
                user_collection.objects.unlink(obj)
            collection.objects.link(obj)
        except ReferenceError:
            print(f"Skipping deleted object: {obj}")
           
def import_gltf(filepath: str, collection = None):
    """Imports GLTF. Returns List of imported objects"""
    scene_obects = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=filepath)  
    
    garbage_collection = bpy.data.collections.get("glTF_not_exported")
    if garbage_collection:
        bpy.data.collections.remove(garbage_collection)
            
    imported_gltf = [obj for obj in bpy.context.scene.objects if obj not in scene_obects]
    
    if collection:
        link_objects_to_collection(imported_gltf, collection)
        
    return imported_gltf

def remove_custom_shapes(armature):
    """Removes custom shapes from all bones in the given armature."""
    if armature.type != "ARMATURE":
        print(f"Object '{armature.name}' is not an armature.")
        return
    
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="POSE")

    for bone in armature.pose.bones:
        if bone.custom_shape:
            print(f"Removing custom shape from bone: {bone.name}")
            bone.custom_shape = None  
            
    bpy.ops.object.mode_set(mode="OBJECT")

def attache_mekrig(armature, racial_code):
    """Imports Mekrig, removes duplicate bones and merges it with any armature present in objects list. Returns Mekrig Armature"""
    if armature:
        mekrig = append_mekrig(racial_code)
         
        merged_armature = merge_armatures(mekrig, armature)
        
        return merged_armature
    return None
    
def create_collection(name="Collection"):
    """Creates a Collection"""
    if name not in bpy.data.collections:
        new_collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(new_collection)
        return new_collection  

    count = 1
    while f"{name}.{count:03d}" in bpy.data.collections:
        count += 1

    new_name = f"{name}.{count:03d}"
    new_collection = bpy.data.collections.new(new_name)
    bpy.context.scene.collection.children.link(new_collection)
    return new_collection 

def get_racial_code(objects, id):
    """Searches for an object containing specified ID in its name and extracts the racial code."""
    for obj in objects:
        if id in obj.name:
            match = re.search(r"c\d{4}", obj.name)
            if match and match.group() in racial_code_to_operator:
                return match.group() 

    return None 

def parent_objects(objects, parent_obj, keep_transform=True):
    """Parents a list of objects to a given parent object."""
    
    bpy.ops.object.mode_set(mode="OBJECT")  

    for obj in objects:
        if obj != parent_obj:  
            obj.parent = parent_obj
            obj.matrix_parent_inverse = parent_obj.matrix_world.inverted() if keep_transform else obj.matrix_parent_inverse

class MEKTOOLS_OT_ImportGLTFFromMeddle(Operator):
    """Import GLTF from Meddle and perform cleanup tasks"""
    bl_idname = "mektools.import_meddle_gltf"
    bl_label = "Import GLTF from Meddle"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default='*.gltf', options={'HIDDEN'})
    
    import_with_shaders_setting: BoolProperty(name="Import with Meddle Shaders", description="Tries to also import all shaders from meddle shader cache", default=True)
    append_mekrig: BoolProperty(name="Appends Mekrig", description="Appends Mekrig, disable for Object import", default=True)
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
        layout.prop(self, "append_mekrig", toggle=False)
        layout.prop(self, "remove_parent_on_poles", toggle=False)

    def execute(self, context):  
        bpy.context.window.cursor_set('WAIT')      

        #base import function
        import_collection = create_collection("Meddle_Import")
        imported_gltf = import_gltf(self.filepath, import_collection)
        
        racial_code_identifier="iri"
        racial_code = get_racial_code(imported_gltf, racial_code_identifier)
        
        gltf_armature = find_armature_in_objects(imported_gltf)
        remove_custom_shapes(gltf_armature)      
        clear_parents_keep_transform(imported_gltf)
        
        working_object_set = merge_by_material(imported_gltf)
        
        #checking for user options
        if self.import_with_shaders_setting:
            import_meddle_shader(self, working_object_set)
        else:
            bpy.ops.mektools.append_shaders()
            bpy.ops.material.material_fixer_auto()
            
        if self.append_mekrig:
            mekrig_armature = attache_mekrig(gltf_armature, racial_code) 
            parent_objects(working_object_set, mekrig_armature)
            if self.remove_parent_on_poles:
                remove_pole_parents(mekrig_armature)   
        
        bpy.ops.object.select_all(action='DESELECT')
        
        self.report({'INFO'}, "GLTF imported and processed successfully.")
        bpy.context.window.cursor_set('DEFAULT')
        bpy.ops.ed.undo_push()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MEKTOOLS_OT_ImportGLTFFromMeddle)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportGLTFFromMeddle)