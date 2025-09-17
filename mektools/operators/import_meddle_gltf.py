import bpy
from bpy.types import Operator
import os
import importlib.util
from bpy.props import BoolProperty, StringProperty
from collections import defaultdict, namedtuple
import re
from ..addon_preferences import get_addon_preferences 
from ..libs import spline_gen, helper

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
        bpy.ops.meddle.import_shaders('EXEC_DEFAULT')  
        bpy.ops.meddle.apply_to_selected('EXEC_DEFAULT', directory=meddle_cache_directory)  
    except Exception as e:
        self.report({'ERROR'}, f"Failed to append Meddle shaders: {e}")
        
def remove_pole_parents(armature):
    """Removes the parent from IK pole bones in the given armature."""
    if armature and armature.type == 'ARMATURE':
        bpy.ops.object.mode_set(mode='EDIT')

        bones_to_unparent = ["IK_Arm_Pole.R", "IK_Arm_Pole.L", "IK_Leg_Pole.R", "IK_Leg_Pole.L"]

        for bone_name in bones_to_unparent:
            if bone_name in armature.data.edit_bones:
                bone = armature.data.edit_bones[bone_name]
                bone.parent = None  

        bpy.ops.object.mode_set(mode='OBJECT')

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
    
    assign_bones_to_collection(armature_b, armature_b.pose.bones, 'Not Mekrig Bones', False)

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
    """Merges objects that share the same material and returns the updated list of all objects, including non-mesh objects that were not modified."""
    material_mesh_groups = defaultdict(list)
    all_objects = set(objects)  

    for obj in objects:
        try:
            if obj.type == "MESH" and obj.data.materials:
                material_name = obj.data.materials[0].name
                material_mesh_groups[material_name].append(obj)
        except ReferenceError:
            print(f"[MekTools] Skipping deleted object: {obj}")

    new_objects = set()  

    for material, meshes in material_mesh_groups.items():
        if len(meshes) < 2:
            new_objects.update(meshes)  # Keep unmerged meshes
            continue
        bpy.ops.object.select_all(action='DESELECT')
        for mesh in meshes:
            mesh.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.join()
        merged_object = bpy.context.view_layer.objects.active
        new_objects.add(merged_object)
        bpy.ops.object.select_all(action='DESELECT')

    non_mesh_objects = set()
    for obj in all_objects:
        try:
            if obj.type != "MESH":
                non_mesh_objects.add(obj)
        except ReferenceError:
            print(f"[MekTools] Skipping deleted object: {obj}")
    
    updated_objects = new_objects | non_mesh_objects  

    return list(updated_objects)

def find_armature_in_objects(objects):
    """Finds the first armature in the objects imported."""
    for obj in objects:
        try:
            if obj.type == 'ARMATURE':
                return obj 
        except ReferenceError:
            print(f"[Mektools] Skipping deleted object: {obj}")  
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
            print(f"[Mektools] Skipping deleted object: {obj}")

def link_objects_to_collection(objects, collection):
    """Links objects to a collection."""
    for obj in objects:
        try:
            for user_collection in obj.users_collection:
                user_collection.objects.unlink(obj)
            collection.objects.link(obj)
        except ReferenceError:
            print(f"[Mektools] Skipping deleted object: {obj}")
           
def import_model(filepath: str, collection=None, pack_images=True, disable_bone_shape=False, merge_vertices=False):
    """Imports GLTF or FBX. Returns list of imported objects."""
    scene_objects = set(bpy.context.scene.objects)
    ext = os.path.splitext(filepath)[1].lower()

    if ext in [".gltf", ".glb"]:
        bpy.ops.import_scene.gltf(
            filepath=filepath,
            import_pack_images=pack_images,
            disable_bone_shape=disable_bone_shape,
            merge_vertices=merge_vertices
        )
        # Remove glTF garbage collection if present
        garbage_collection = bpy.data.collections.get("glTF_not_exported")
        if garbage_collection:
            bpy.data.collections.remove(garbage_collection)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=filepath)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    imported_objs = [obj for obj in bpy.context.scene.objects if obj not in scene_objects]

    if collection:
        link_objects_to_collection(imported_objs, collection)

    return imported_objs

def remove_custom_shapes(armature):
    """Removes custom shapes from all bones in the given armature."""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="POSE")

    for bone in armature.pose.bones:
        if bone.custom_shape:
            bone.custom_shape = None  
            
    bpy.ops.object.mode_set(mode="OBJECT")

def assign_bones_to_collection(armature, bones, collection_name, is_visible = bool, bone_keywords = None):
    """Searches for bones in a given list that contain specified keywords. Can set Bone Collection and Collection-Visibilty state. Returns assigned Bones"""

    bpy.ops.object.mode_set(mode='OBJECT')

    bone_collection = None
    for coll in armature.data.collections:  
        if coll.name == collection_name:
            bone_collection = coll
            break

    if not bone_collection:
        bone_collection = armature.data.collections.new(name=collection_name)

    bpy.ops.object.mode_set(mode='POSE') 

    assigned_bones = []
    for bone in bones:
        try:
            if bone_keywords:
                if any(keyword in bone.name for keyword in bone_keywords):  
                    bone_collection.assign(bone)  
                    assigned_bones.append(bone.name)
            elif bone_keywords == None:
                bone_collection.assign(bone)  
                assigned_bones.append(bone.name)
        except ReferenceError:
            print(f"[Mektools] ⚠️ Skipping deleted bone: {bone}")
            
    bone_collection.is_visible = is_visible
            
    bpy.ops.object.mode_set(mode='OBJECT')
    return assigned_bones
    
def attache_mekrig(armature, racial_code):
    """Appends Mekrig, merges diff between armature and mekrig while keeping parents. Returns merged armature"""
    if armature:
        mekrig = append_mekrig(racial_code)
        
        #resets pose before merging with mekrig
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        bpy.ops.pose.reset()
        
        merged_armature = merge_armatures(mekrig, armature)
        hair_bones = assign_bones_to_collection(merged_armature, merged_armature.pose.bones, 'Hair', True, ['j_ex', 'j_kami'])
        assign_bones_to_collection(merged_armature, merged_armature.pose.bones, 'Physic',False, ['phys'])
        assign_bones_to_collection(merged_armature, merged_armature.pose.bones, 'IVCS', False, ['iv_'])
        
        set_bone_display(merged_armature, hair_bones, 'cs.hair', 'THEME01')
        
        return merged_armature
    return None
    
def get_racial_code(objects, id):
    """Searches for an object containing specified ID in its name and extracts the racial code."""
    # First, try to find the racial code in the object names
    for obj in objects:
        if id in obj.name:
            match = re.search(r"c\d{4}", obj.name)
            if match and match.group() in racial_code_to_operator:
                return match.group()

    # If not found, try to find an object with a material containing the racial code
    iri_object = next(
        (obj for obj in bpy.data.objects if any("iri" in (mat.name if mat else "") for mat in obj.material_slots)),
        None
    )

    if iri_object:
        for code in racial_code_to_operator:
            if any(code in (mat.name if mat else "") for mat in iri_object.material_slots):
                return code

    return None

def parent_objects(objects, parent_obj, keep_transform=True):
    """Parents a list of objects to a given parent object."""
    bpy.ops.object.mode_set(mode="OBJECT")  

    for obj in objects:
        try:
            if obj != parent_obj:  
                obj.parent = parent_obj
                obj.matrix_parent_inverse = parent_obj.matrix_world.inverted() if keep_transform else obj.matrix_parent_inverse
        except ReferenceError:
            print(f"[Mektools] Skipping deleted object: {obj}")        

def merge_by_name(objects, name_filter):
    """Merges all objects in the given list that contain the specified name_filter in their name. Returns an updated object list."""
    filtered_objects = [obj for obj in objects if name_filter.lower() in obj.name.lower() and obj.type == "MESH"]
    
    updated_objects = set(objects)

    if len(filtered_objects) < 2:
        return list(updated_objects)  

    bpy.ops.object.select_all(action='DESELECT')  
    for obj in filtered_objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = filtered_objects[0]  
    bpy.ops.object.join() 

    merged_object = bpy.context.view_layer.objects.active

    updated_objects.difference_update(filtered_objects)  
    updated_objects.add(merged_object) 

    bpy.ops.object.select_all(action='DESELECT') 

    return list(updated_objects)  

def get_collection(object):
    """Returns the collection that contains this object."""
    for collection in bpy.data.collections:
        if any(object is coll_obj for coll_obj in collection.objects): 
            return collection  
    return None  

def link_to_collection(objects, collection):
    for obj in objects:
        try: 
            for coll in list(obj.users_collection): 
                coll.objects.unlink(obj)
                collection.objects.link(obj)  
        except ReferenceError:
            print(f"[Mektools] Skipping deleted object: {obj}")
                    
def unlink_from_collection(collection):
    """Unlinks all objects and sub-collections from the given collection while keeping the objects in the scene."""
    scene_collection = bpy.context.scene.collection  

    for obj in list(collection.objects): 
        collection.objects.unlink(obj)  
        scene_collection.objects.link(obj) 
            
    for sub_collection in list(collection.children):       
        collection.children.unlink(sub_collection)  
        scene_collection.children.link(sub_collection)
                
def delete_rna_from_objects(objects):
    new_objects = set()
    for obj in objects:
        try:
            if obj.name:
                new_objects.add(obj)
        except ReferenceError:
            pass    
    return new_objects

def set_bone_display(armature, bones, cs_bone_name = None, theme = None):
    bpy.ops.object.mode_set(mode='POSE')
    cs_obj = None
    if cs_bone_name:
        cs_obj = bpy.data.objects.get(cs_bone_name)
    for bone_name in bones:
        pose_bone = armature.pose.bones.get(bone_name)
        if pose_bone:
            if cs_obj:
                pose_bone.custom_shape = cs_obj
            if theme:
                pose_bone.color.palette = theme 
    bpy.ops.object.mode_set(mode='OBJECT')


class MEKTOOLS_OT_ImportGLTFFromMeddle(Operator):
    """Import GLTF from Meddle and perform cleanup tasks"""
    bl_idname = "mektools.import_meddle_gltf"
    bl_label = "Meddle Import"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(subtype="FILE_PATH")  # type: ignore
    filter_glob: StringProperty(default='*.gltf;*.glb;*.fbx', options={'HIDDEN'})  # type: ignore
    
    s_pack_images: BoolProperty(name="Pack-Images", description="Pack all Images into .blend file", default=True)  # type: ignore
    s_merge_vertices: BoolProperty(name="Merge Vertices", description="The glTF format requires discontinuous normals, UVs, and other vertex attributes to be stored as separate vertices, as required for rendering on typical graphics hardware. This option attempts to combine co -located vertices where possible. Currently cannot combine verts with different normals.", default=False)  # type: ignore
    s_import_collection: BoolProperty(name="Import-Collection", description="Stores all import in a seperatre Collection", default=False)  # type: ignore
    
    s_merge_skin: BoolProperty(name="Merge Skin", description="Merges all skin objects", default=True)  # type: ignore
    s_merge_by_material: BoolProperty(name="Merge by Material", description="Merges all objects with the same material", default=True)  # type: ignore
    
    s_import_with_shaders_setting: BoolProperty(name="Import with Meddle Shaders", description="Tries to also import all shaders from meddle shader cache", default=True)  # type: ignore
        
    s_disable_bone_shape: BoolProperty(name="Disable Bone Shapes", description="Disables the generation of Bone Shapes on Import", default=True)  # type: ignore
    
    s_remove_parent_on_poles: BoolProperty(name="Remove Parents from Pole-Targets", description="Removes the Parent from Pole-Targets", default=False)  # type: ignore
    s_spline_tail: BoolProperty(name="Generate spline Tail", description="Generates and replaces the tail with Spline IKs", default=False)  # type: ignore
    s_spline_gear: BoolProperty(name="Generate spline Gear", description="Generates and replaces the gear with Spline IKs", default=False)  # type: ignore
    
    s_is_pinned:  BoolProperty(name="Is Pinned", description="Pinns the imported object", default=True)  # type: ignore
    s_obj_name: StringProperty(name="Object Name", description="Set a name for the imported object", default="")  # type: ignore
    
    s_armature_type: bpy.props.EnumProperty(
        name="Armature Type",
        description="Choose the armature type",
        items=[
            ("Vanilla", "Vanilla", "Use the default armature setup"),
            ("Mekrig", "Mekrig", "Use the Mekrig armature setup"),
        ],
        default="Mekrig"
    )# type: ignore
    
    def invoke(self, context, event):
        self.prefs = get_addon_preferences()
        if self.prefs.default_meddle_import_path:
            self.filepath = self.prefs.default_meddle_import_path
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        indent = 0.3
        indent_nested = 0.3
        layout = self.layout

        # 🔹 Import Settings Title
        layout.label(text="Import Settings", icon="PREFERENCES")

        # 🔹 Import Options Section
        box = layout.box()
        row = box.row()
        row.label(text="GLTF Import", icon="IMPORT")

        col = box.column(align=True)
    
        split = col.split(factor=indent)
        split.label(text=" ")
        split.prop(self, "s_pack_images")
        
        split = col.split(factor=indent)
        split.label(text=" ")
        split.prop(self, "s_merge_vertices")

        split = col.split(factor=indent)  
        split.label(text=" ")
        split.prop(self, "s_import_collection")
        
        # 🔹 Mesh Options Section
        box = layout.box()
        row = box.row()
        row.label(text="Mesh Options", icon="MESH_DATA")

        col = box.column(align=True)
    
        split = col.split(factor=indent)
        split.label(text=" ")
        split.prop(self, "s_merge_skin")

        split = col.split(factor=indent)  
        split.label(text=" ")
        split.prop(self, "s_merge_by_material")

        # 🔹 Shaders Section
        box = layout.box()
        row = box.row()
        row.label(text="Shaders", icon="SHADING_RENDERED")

        col = box.column(align=True)
        split = col.split(factor=indent)  
        split.label(text=" ")
        split.prop(self, "s_import_with_shaders_setting")

        # 🔹 Armature Section
        box = layout.box()
        row = box.row()
        row.label(text="Armature", icon="ARMATURE_DATA")

        col = box.column(align=True)
        split = col.split(factor=indent)  
        split.label(text=" ")
        split.prop(self, "s_disable_bone_shape")

        # 🔹 Armature Type Selection (Vanilla vs Mekrig)
        row = box.row()
        split = row.split(factor=indent)
        split.label(text="Armature Type:")
        row = split.row(align=True)
        row.prop(self, "s_armature_type", expand=True)
        
        col = box.column(align=True)
        col.active = self.s_armature_type == 'Mekrig'
        split = col.split(factor=indent_nested)  
        split.label(text=" ")
        split.prop(self, "s_remove_parent_on_poles")

        if self.prefs.ex_button_spline_tail == 'ON':
            split = col.split(factor=indent_nested)  
            split.label(text=" ")
            split.prop(self, "s_spline_tail")

        if self.prefs.ex_button_spline_gear == 'ON':
            split = col.split(factor=indent_nested)  
            split.label(text=" ")
            split.prop(self, "s_spline_gear")
           
        # 🔹 Pin Section 
        box = layout.box()
        row = box.row()
        row.label(text="Pin", icon="PINNED")
        
        col = box.column(align=True)
        
        split = col.split(factor=indent)  
        split.label(text=" ")
        split.prop(self, "s_is_pinned")
        
        col = box.column(align=True)
        split = col.split(factor=indent)  
        split.label(text="Object Name")
        split.prop(self, "s_obj_name", text=" ")


    def execute(self, context):  
        bpy.context.window.cursor_set('WAIT')   
        
        if not self.filepath or not (self.filepath.lower().endswith(".gltf") or self.filepath.lower().endswith(".glb") or self.filepath.lower().endswith(".fbx")): 
            self.report({'ERROR'}, "Please select a File")
            return {'CANCELLED'}   

        #base import function
        import_collection = helper.create_collection("Model_Import")
        import_collection.color_tag = "COLOR_05"
        object_set = import_model(self.filepath, import_collection, self.s_pack_images, self.s_disable_bone_shape, self.s_merge_vertices)
        
        racial_code_identifier="iri"
        racial_code = get_racial_code(object_set, racial_code_identifier)
        
        armature = find_armature_in_objects(object_set)  
        
        if self.s_merge_by_material:
            object_set = merge_by_material(object_set)
        
        if self.s_merge_skin:
            object_set = merge_by_name(object_set, 'skin')
        
        
        # remove animation track from the imported objects
        # if animation data exists, apply the scaling directly to the bones and remove the pose afterwards
        bone_scales = {}
        if armature.pose and armature.pose.bones:
            for bone in armature.pose.bones:
                try:
                    bone_scales[bone.name] = bone.scale.copy()  # Store the original scale of the bone
                except ReferenceError:
                    print(f"[Mektools] Skipping deleted bone: {bone}")
        
            for obj in object_set:
                try:
                    if obj.animation_data and obj.animation_data.action:
                        # Apply scaling to bones if animation data exists
                        obj.animation_data.action = None
                        
                    if obj.animation_data and obj.animation_data.nla_tracks:
                        for nt in obj.animation_data.nla_tracks:
                            obj.animation_data.nla_tracks.remove(nt)
                except ReferenceError:
                    print(f"[Mektools] Skipping deleted object: {obj}")
        
        #checking for user options
        if self.s_import_with_shaders_setting:
            try:
                import_meddle_shader(self, object_set)
            except Exception as e:
                self.report({'ERROR'}, f"[Mektools] Failed to import Meddle shaders. Applying default shaders instead: {e}")
                bpy.ops.mektools.append_shaders()
                bpy.ops.material.material_fixer_auto()
        else:
            bpy.ops.mektools.append_shaders()
            bpy.ops.material.material_fixer_auto()
            
        #armature setup  
        if self.s_armature_type == 'Mekrig':
            clear_parents_keep_transform(object_set)
            armature = attache_mekrig(armature, racial_code) 
            mekrig_collection = get_collection(armature)
            mekrig_collection.color_tag = "COLOR_01"
            
            object_set = delete_rna_from_objects(object_set) # this is just for sanity
            link_to_collection(object_set, mekrig_collection)
            parent_objects(object_set, armature)
            
            if self.s_remove_parent_on_poles:
                remove_pole_parents(armature)  
                
            if self.s_spline_tail:
                reference_bones = ["n_sippo_a", "n_sippo_b", "n_sippo_c", "n_sippo_d", "n_sippo_e"]
                spline_gen.generatr_tail_spline_ik(
                    armature=armature,
                    reference_bone_names=reference_bones,
                    curve_name="TailCurve"
                )
            armature.data["mektools_armature_type"] = "mekrig"
            
        armature.name = self.s_obj_name if self.s_obj_name != "" else armature.name 

        if armature.pose and armature.pose.bones:
            # apply bone scales to the armature
            for bone in armature.pose.bones:
                try:
                    if bone.name in bone_scales:
                        bone.scale = bone_scales[bone.name]  # Apply the stored scale to the bone
                except ReferenceError:
                    print(f"[Mektools] Skipping deleted bone: {bone}")
        
        if self.s_is_pinned:
            if self.prefs.ex_pins == 'ON': 
                new_pin = context.scene.pins.add()
                new_pin.object = armature
             
        if not self.s_import_collection:
            unlink_from_collection(import_collection)
            bpy.data.collections.remove(import_collection) 
        
        bpy.ops.object.select_all(action='DESELECT')
        
        self.report({'INFO'}, "Model imported and processed successfully.")
        bpy.context.window.cursor_set('DEFAULT')
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MEKTOOLS_OT_ImportGLTFFromMeddle)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportGLTFFromMeddle)