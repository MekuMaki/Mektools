import bpy
from bpy.types import Operator
import os
import importlib.util
from math import radians
from bpy.props import BoolProperty
from collections import defaultdict, namedtuple
from ..addon_preferences import get_addon_preferences 


# Load the bone names from bone_names.py in the data folder
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data")
BONE_NAMES_FILE = os.path.join(DATA_PATH, "bone_names.py")

MekrigData = namedtuple("MekrigData", ["armature", "collection"])

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

def filter_bones(objects_to_filter, mesh_filter_string, bone_names_to_skip = []):
    """Returns a set of bone names that influence meshes whose name contains the mesh_filter_string. Needs Refactor or delete"""
    bpy.ops.object.mode_set(mode='OBJECT')

    filtered_objects = [obj for obj in objects_to_filter if mesh_filter_string in obj.name]
    influential_bones = set()
    for obj in filtered_objects:
        for vgroup in obj.vertex_groups:
            if vgroup.name in bone_names_to_skip:  
                continue
            if any(vgroup.index in [g.group for g in v.groups if g.weight > 0] for v in obj.data.vertices):
                influential_bones.add(vgroup.name)

    return influential_bones

def append_mekrig(objects, racial_code_identifier="iri"):
    """Appends the correct Mekrig depending on Racial Code"""

    scene_collections_before = set(bpy.data.collections)

    racial_code_object = next(
        (obj for obj in objects if racial_code_identifier in obj.name or any(racial_code_identifier in mat.name for mat in obj.material_slots)),
        None
    )

    for code in racial_code_to_operator:
        if code in racial_code_object.name:
            operator_id = racial_code_to_operator[code]
            eval(f"bpy.ops.{operator_id}()")
            break

    scene_collections_after = set(bpy.data.collections)
    imported_collection = scene_collections_after - scene_collections_before
    
    if not imported_collection:
        return MekrigData(None, None)
    
    for obj in imported_collection.objects:
        if obj.type == "ARMATURE":
            return MekrigData(obj, imported_collection)
    
    return MekrigData(None, imported_collection)

def merge_armatures(armature_a, armature_b ):
    """Merges armature A with armature B. Returns B"""
    
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    #set_armature_modifier_target(objects_imported, mekrig_armature)

    #deselect all to ensure only the armatures are selected
    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.view_layer.objects.active = armature_a
    armature_a.select_set(True)
    armature_b.select_set(True)
    bpy.ops.object.join()    

    #ima be real idk why we rotate the bones here but we do
    #bpy.ops.object.mode_set(mode='EDIT')
    #mek_kao_bone = mekrig_armature.data.edit_bones.get("mek kao")
    #for bone in mekrig_armature.data.edit_bones:
    #    if bone.name in influential_bones:
    #        bone.parent = mek_kao_bone
    #        bone.roll = radians(90)

    bpy.ops.object.mode_set(mode='OBJECT')

    return armature_b

def set_armature_modifier_target(objects_to_set_target, armature_target):
    for mesh in objects_to_set_target:
        if mesh.type == 'MESH':
            mesh.select_set(True)   

    armature_target.select_set(True)
    bpy.context.view_layer.objects.active = armature_target
    bpy.ops.object.parent_set(type='OBJECT')

    # set armature modifier to mekrig_armature
    for mesh in objects_to_set_target:
        if mesh.type == 'MESH':
            for mod in mesh.modifiers:
                if mod.type == 'ARMATURE': 
                    mod.object = armature_target
                      
def merge_by_material(objects):
    """Merges objects with same material"""
    material_mesh_groups = defaultdict(list)

    for obj in objects:
        try:
            if obj.type == "MESH" and obj.data.materials:
                material_name = obj.data.materials[0].name 
                material_mesh_groups[material_name].append(obj)
        except ReferenceError:
            print(f"Skipping deleted object: {obj}")  

    for material, meshes in material_mesh_groups.items():
        if len(meshes) < 2: 
            continue

        print(f"[Mektools] Merging {len(meshes)} meshes with material: {material}")

        bpy.ops.object.select_all(action='DESELECT')
        for mesh in meshes:
            mesh.select_set(True)
            
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.join()
        bpy.ops.object.select_all(action='DESELECT')

def find_armature_in_objects(objects):
    """Finds the first armature in the objects imported."""
    for obj in objects:
        try:
            if obj.type == 'ARMATURE':
                return obj 
        except ReferenceError:
            print(f"Skipping deleted object: {obj}")
       
    return None

def rebuild_objects_imported(objects_before_import):
    """Rebuilds the list of objects imported.

    :param objects_before_import: objects before the import
    :type objects_before_import: list
    :return: objects imported
    :rtype: list
    """

    #we create a list of objects that were i mported by substracting the
    #objects before the import from the objects after the import
    #and the difference (substraction) between the two is the objects that were imported
    #substracting sets is basic boolean math, btw
    objects_imported = set(bpy.data.objects) - objects_before_import
    return objects_imported

def get_bones_by_name(armature, name):
    """Returns a list of bone names that contain the nameStr in their name."""
    if armature and armature.type == "ARMATURE":
        return [bone for bone in armature.data.bones if name in bone.name]
    return []

def remove_duplicate_bones(armature_a, armature_b):
    """Remove bones present in armature B from armature A. Returns edited Armature A"""
    
    bpy.context.view_layer.objects.active = armature_a
    bpy.ops.object.mode_set(mode='EDIT')
    
    reference_bones = {bone.name for bone in armature_b.data.bones}
    
    for bone in armature_a.data.edit_bones[:]:
        if bone.name in reference_bones:
            armature_a.data.edit_bones.remove(bone)
            print(f"[Mektools] Removed duplicate bone: {bone.name}")
 
    #mekrig_coverage = set(load_bone_names()) 
    #for bone_name in mekrig_coverage:
    #    if bone_name in armature.data.edit_bones:
    #        armature.data.edit_bones.remove(armature.data.edit_bones[bone_name])

    #i dont know why this even exists. This basicly removes all bones except the hair bones ? so why ? why then even do the ode above ? i would want that anyway since keeping bones that we dont cover isnt a bad thing 
    #hair_bones = filter_bones(objects, "hir")
    #bpy.ops.object.mode_set(mode='EDIT')
    #for bone in armature.data.edit_bones:
    #    if bone.name not in hair_bones:
    #        armature.data.edit_bones.remove(bone)

    #This certainly imo shoulkdnt be here, ill have to look later where to put it.
    #cs_hair = next((obj for obj in objects if  "cs.hair" in obj.name), None)
    #cs_hair_bones = get_bones_by_name(armature, "j_ex")
    #set_custom_bone_display(cs_hair_bones, cs_hair, 'THEME01')

    bpy.ops.object.mode_set(mode='OBJECT')

    return armature_a

def set_custom_bone_display(bones, custom_shape, theme):
    # Switch to Pose Mode for hair bone adjustments
    bpy.ops.object.mode_set(mode='POSE')
    for bone in bones:
        print("Searching for bone: ", bone.name)
        if bone:
            print("Found bone: ", bone.name)
            bone.custom_shape = custom_shape
            print("Setting custom shape to: ", custom_shape.name)
            bone.color.palette = theme 

def clear_parents_keep_transform(objects_to_clear):
    """Clears the parent of the objects and keeps the transform."""
    for obj in objects_to_clear:
        try:
            obj.select_set(True)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            obj.select_set(False)
        except ReferenceError:
            print(f"Skipping deleted object: {obj}")

def link_objects_to_collection(objects_to_link, collection_to_link_to):
    """Links objects to a collection."""
    for obj in objects_to_link:
        try:
            for collection in obj.users_collection:
                collection.objects.unlink(obj)
            
            collection_to_link_to.objects.link(obj)
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
        link_objects_to_collection(import_gltf, collection)
        
    return imported_gltf

def remove_icospheres(imported_gltf):
    """Removes Icospheres from OBJECTS. Returns new set of OBJECTS"""
    filtered_gltf = []

    for obj in imported_gltf:
        if obj.type == "MESH" and "Icosphere" in obj.name:
            bpy.data.objects.remove(obj)
        else:
            filtered_gltf.append(obj)

    return filtered_gltf

def attache_mekrig(objects):
    """Imports Mekrig, removes duplicate bones and merges it with any armature present in objects list. Returns Mekrig Armature"""
    gltf_armature = find_armature_in_objects(objects)
     
    if gltf_armature:
        mekrig = append_mekrig(objects)

        stripped_gltf_armature = remove_duplicate_bones(gltf_armature, mekrig.armature)
        
        merged_armature = merge_armatures(mekrig.armature, stripped_gltf_armature)
        
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

        scene_objects = set(bpy.data.objects)
        
        #base import function
        import_collection = create_collection("Meddle_Import")
        imported_gltf = import_gltf(self.filepath, import_collection)      
        working_object_set = remove_icospheres(imported_gltf)
        clear_parents_keep_transform(working_object_set)
        merge_by_material(working_object_set)
        
        
        #checking for user options
        if self.import_with_shaders_setting:
            import_meddle_shader(self, working_object_set)
        else:
            bpy.ops.mektools.append_shaders()
            bpy.ops.material.material_fixer_auto()
            
        if  self.append_mekrig:
            
            mekrig_armature = attache_mekrig(working_object_set) 
            
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