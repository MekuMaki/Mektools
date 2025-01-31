import bpy
import json
import mathutils
import re
from bpy.types import Operator
from mathutils import Matrix, Quaternion
from mathutils import Vector
from . import pose_helper

collection_visibility = {}

def set_pole_targets(armature):
    print("Moving pole targets to their respective IK bones...")

    for bone in armature.pose.bones:
        for constraint in bone.constraints:
            if constraint.type == 'IK':
                print(f"Processing IK constraint on bone '{bone.name}'...")

                if not constraint.pole_target or not constraint.pole_subtarget:
                    print(f"No valid pole target or subtarget for IK constraint on bone '{bone.name}'. Skipping.")
                    continue

                pole_target = armature.pose.bones.get(constraint.pole_subtarget)
                if not pole_target:
                    print(f"Pole target bone '{constraint.pole_subtarget}' not found. Skipping.")
                    continue

                pole_target.matrix.translation = bone.matrix.translation
                print(f"Moved pole target '{pole_target.name}' to position of IK bone '{bone.name}'.")

    print("Pole targets moved successfully.")    

def reverse_constraints(armature):
    print("Reversing constraints...")

    arm = armature.pose
    
    sorted_bones = []

    def collect_bones_recursive(bone):
        sorted_bones.append(bone)
        for child in bone.children:
            collect_bones_recursive(child)
            
    for bone in arm.bones:
        if bone.parent is None:
            collect_bones_recursive(bone)

    for bone in sorted_bones:
        for constraint in bone.constraints:
            if constraint.type in {'COPY_LOCATION', 'COPY_ROTATION', "COPY_TRANSFORMS"}:
                print(f"Reversing constraint '{constraint.name}' on bone '{bone.name}'")

                original_target = constraint.target
                target_bone_name = constraint.subtarget

                if not original_target or not target_bone_name:
                    print(f"Constraint '{constraint.name}' on bone '{bone.name}' has no valid target. Skipping.")
                    continue

                target_bone = original_target.pose.bones.get(target_bone_name)
                if not target_bone:
                    print(f"Target bone '{target_bone_name}' not found. Skipping constraint '{constraint.name}'.")
                    continue

                new_constraint = target_bone.constraints.new(type=constraint.type)
                new_constraint.target = armature
                new_constraint.subtarget = bone.name 
                
                
                new_constraint.target_space = constraint.target_space
                new_constraint.owner_space = constraint.owner_space
                new_constraint.influence = constraint.influence
                
                if constraint.type == "COPY_TRANSFORMS":
                    new_constraint.mix_mode = constraint.mix_mode
                    new_constraint.remove_target_shear = constraint.remove_target_shear
                
                if constraint.type == "COPY_ROTATION":
                    new_constraint.mix_mode = constraint.mix_mode
                    new_constraint.euler_order = constraint.euler_order  
                    new_constraint.use_x = constraint.use_x
                    new_constraint.use_y = constraint.use_y
                    new_constraint.use_z = constraint.use_z    
                    new_constraint.invert_x = constraint.invert_x
                    new_constraint.invert_y = constraint.invert_y
                    new_constraint.invert_z = constraint.invert_z
                    
                if constraint.type == "COPY_LOCATION":
                    new_constraint.use_offset = constraint.use_offset
                    new_constraint.use_x = constraint.use_x
                    new_constraint.use_y = constraint.use_y
                    new_constraint.use_z = constraint.use_z    
                    new_constraint.invert_x = constraint.invert_x
                    new_constraint.invert_y = constraint.invert_y
                    new_constraint.invert_z = constraint.invert_z

                # Apply the constraint on the target bone
                bpy.ops.object.mode_set(mode='POSE')
                bpy.ops.pose.select_all(action='DESELECT')
                target_bone.bone.select = True
                bpy.ops.pose.visual_transform_apply()
                target_bone.constraints.remove(new_constraint)

                print(f"Constraint reversed and applied on '{target_bone_name}'.")

    print("Constraints reversed successfully.")
    
def reset_bones_in_collections(armature, collection_names, force_reset):
    if isinstance(collection_names, str):
        collection_names = [collection_names]

    print(f"Resetting rotations for bones in collections: {collection_names}...")

    for collection_name in collection_names:
        bone_collection = armature.data.collections_all.get(collection_name)
        if not bone_collection:
            print(f"Bone collection '{collection_name}' not found. Skipping.")
            continue
        
        if not bone_collection.is_visible:
            print(f"Bone collection '{collection_name}' is hidden. Unhiding for processing.")
            bone_collection.is_visible = True

        for bone in bone_collection.bones:
            pose_bone = armature.pose.bones.get(bone.name)
            if pose_bone:
                has_valid_constraint = any(
                    constraint.type in {'COPY_ROTATION', 'COPY_LOCATION', 'COPY_TRANSFORMS'}
                    for constraint in pose_bone.constraints
                )
                
                if has_valid_constraint or force_reset:
                    print(f"Resetting rotation for bone '{pose_bone.name}' in collection '{collection_name}'...")
                    pose_bone.rotation_quaternion = Quaternion((1, 0, 0, 0))
    
    print("Rotation reset completed.")

class POSE_OT_LoadBone(bpy.types.Operator):
    """Load a single bone from the current .pose file to the current armature"""
    bl_idname = "pose.load_bone"
    bl_label = "Load Bone"
    bl_options = {'REGISTER', 'UNDO'}

    bone: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    diff: bpy.props.FloatVectorProperty(size=4)

    def strip_suffix(self, name):
        """Remove any .xxx suffix from the bone name."""
        return re.sub(r'\.\d+$', '', name)

    def execute(self, context):
        arm = context.object.pose

        print("Bone:", self.bone)
        print("Path:", self.path)
        print("Diff:", self.diff)

        # Strip suffix from the provided bone name
        stripped_bone_name = self.strip_suffix(self.bone)

        with open(self.path, 'r') as f:
            pose = json.load(f)['Bones']

        # Search for the bone in the armature, matching without suffix
        bone = next((b for b in arm.bones if self.strip_suffix(b.name) == stripped_bone_name), None)
        if not bone:
            print(f"Bone '{stripped_bone_name}' not found in the armature.")
            return {'FINISHED'}

        # Get the transformation data for the bone
        trans = pose.get(stripped_bone_name)
        if not trans:
            print(f"Bone '{stripped_bone_name}' not found in the pose file.")
            return {'FINISHED'}

        # Apply rotation
        try:
            rot = trans["Rotation"].split(", ")
            rot = [float(x) for x in rot]
            # Convert XYZW to WXYZ
            rot.insert(0, rot.pop())
            diff_quat = Quaternion(self.diff[:3], self.diff[3])
            rot = Quaternion(rot) @ diff_quat
            bone.rotation_quaternion = context.object.convert_space(
                pose_bone=bone,
                matrix=rot.to_matrix().to_4x4(),
                from_space='POSE',
                to_space='LOCAL'
            ).to_quaternion()
        except Exception as e:
            print(f"Failed to apply rotation: {e}")
            return {'ERROR'}

        print(f"Successfully loaded bone: {self.bone}")
        return {'FINISHED'}
    
def import_pose(filepath, armature):
    print("Starting pose import process...")
    
    bpy.ops.pose.reset()
    
    arm = armature.pose

    # Support for proper bone orientations: get diff from original
    root_bone = arm.bones.get("n_throw")
    if not root_bone:
        print("Root bone 'n_throw' not found.")
        return

    root_bone.matrix_basis = Matrix()
    aa = Quaternion([1, 0, 0, 0]).rotation_difference(root_bone.matrix.to_quaternion()).to_axis_angle()
    diff = [aa[0][0], aa[0][1], aa[0][2], aa[1]]

    # Temporarily disable all constraints
    for bone in arm.bones:
        for constraint in bone.constraints:
            constraint.mute = True
            
    # Apply pose data
    for bone in arm.bones:
        bpy.ops.pose.load_bone('EXEC_DEFAULT', bone=bone.name, path=filepath, diff=diff)
        
        
    # Reverse constraints
    reverse_constraints(armature)
    
    #Pole target Calculation and Adjustment
    set_pole_targets(armature)

    # Re-enable constraints
    for bone in arm.bones:
        for constraint in bone.constraints:
            constraint.mute = False
               
    reset_bones_in_collections(armature, ["Base Bones", "DT Face Bones"], False)
    reset_bones_in_collections(armature, ["IK MCH Bones", "Mouth Controls"], True)
            
    # Reset root bone rotation
    root_bone.rotation_quaternion = Quaternion([1, 0, 0, 0])
    print("Pose import completed successfully.")
    
    return {'FINISHED'}

def store_collection_visibility(collection):
    """Recursively stores visibility states of collections and their parents"""
    collection_visibility[collection.name] = {
        "visible": collection.is_visible,
        "parent": collection.parent.name if collection.parent else None
    }
    for sub_collection in collection.children:
        store_collection_visibility(sub_collection)
        
def restore_collection_visibility(collection, armature):
    """Recursively restores visibility states of collections"""
    if collection.name in collection_visibility:
        stored_state = collection_visibility[collection.name]
        parent_name = stored_state["parent"]
        
        if parent_name and parent_name in [c.name for c in armature.data.collections_all]:
            parent_collection = next(c for c in armature.data.collections_all if c.name == parent_name)
            restore_collection_visibility(parent_collection, armature)

        collection.is_visible = stored_state["visible"]   
    
class IMPORT_POSE_OT(Operator):
    """Import Pose File this is experimental. Face bones are not properly calculatyed rn"""
    bl_idname = "pose.import"
    bl_label = "Import Pose File"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default='*.pose', options={'HIDDEN'})
    
    def invoke(self, context, event):
        prefs = context.preferences.addons["Mektools"].preferences 
        if prefs.default_pose_import_path:
            self.filepath = prefs.default_pose_import_path
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        armature = context.object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected.")
            return {'CANCELLED'}
        
        bpy.context.window.cursor_set('WAIT')
        
        # Store visibility states of all collections
        for collection in armature.data.collections_all:
            store_collection_visibility(collection)

        # Enable all collections
        for collection in armature.data.collections_all:
            collection.is_visible = True
            
        # Import the pose
        import_pose(self.filepath, armature)
        
        # Restore all collections properly
        for collection in armature.data.collections_all:
            restore_collection_visibility(collection, armature)
                
        bpy.context.window.cursor_set('DEFAULT')
        bpy.ops.ed.undo_push()
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(IMPORT_POSE_OT)
    bpy.utils.register_class(POSE_OT_LoadBone)

def unregister():
    bpy.utils.unregister_class(IMPORT_POSE_OT)
    bpy.utils.unregister_class(POSE_OT_LoadBone)
