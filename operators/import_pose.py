import bpy
import json
import mathutils
from mathutils import Matrix, Quaternion
from mathutils import Vector

def set_pole_targets(armature):
    """
    Move the pole targets to the position of their respective IK bones.
    """
    print("Moving pole targets to their respective IK bones...")

    for bone in armature.pose.bones:
        for constraint in bone.constraints:
            if constraint.type == 'IK':
                print(f"Processing IK constraint on bone '{bone.name}'...")

                # Check if the constraint has a valid pole target and subtarget
                if not constraint.pole_target or not constraint.pole_subtarget:
                    print(f"No valid pole target or subtarget for IK constraint on bone '{bone.name}'. Skipping.")
                    continue

                # Get the pole target pose bone
                pole_target = armature.pose.bones.get(constraint.pole_subtarget)
                if not pole_target:
                    print(f"Pole target bone '{constraint.pole_subtarget}' not found. Skipping.")
                    continue

                # Move the pole target to the IK bone's head position
                pole_target.matrix.translation = bone.matrix.translation
                print(f"Moved pole target '{pole_target.name}' to position of IK bone '{bone.name}'.")

    print("Pole targets moved successfully.")    

def reverse_constraints(armature):
    """
    Reverse Copy Location and Copy Rotation constraints from source to target,
    processing bones in parent-to-child order.
    """
    print("Reversing constraints...")

    arm = armature.pose

    # Create a list of bones sorted in parent-to-child order
    sorted_bones = []

    def collect_bones_recursive(bone):
        sorted_bones.append(bone)
        for child in bone.children:
            collect_bones_recursive(child)

    # Start with root bones (bones without a parent)
    for bone in arm.bones:
        if bone.parent is None:
            collect_bones_recursive(bone)

    # Process the bones in the collected order
    for bone in sorted_bones:
        for constraint in bone.constraints:
            if constraint.type in {'COPY_LOCATION', 'COPY_ROTATION', "COPY_TRANSFORMS"}:
                print(f"Reversing constraint '{constraint.name}' on bone '{bone.name}'")

                # Identify the target bone
                original_target = constraint.target
                target_bone_name = constraint.subtarget

                if not original_target or not target_bone_name:
                    print(f"Constraint '{constraint.name}' on bone '{bone.name}' has no valid target. Skipping.")
                    continue

                # Get the target bone
                target_bone = original_target.pose.bones.get(target_bone_name)
                if not target_bone:
                    print(f"Target bone '{target_bone_name}' not found. Skipping constraint '{constraint.name}'.")
                    continue

                # Create a new constraint on the target bone
                new_constraint = target_bone.constraints.new(type=constraint.type)
                new_constraint.target = armature
                new_constraint.subtarget = bone.name  # Reverse the target
                
                
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
    
def reset_bones_in_collections(armature, collection_names):
    """
    Resets the rotation of bones in the specified bone collections to (w=1, x=0, y=0, z=0) in local space.
    Only affects bones with constraints of type COPY_ROTATION, COPY_LOCATION, or COPY_TRANSFORMS.
    
    :param armature: The armature object to process.
    :param collection_names: A single collection name (str) or a list of collection names (list[str]).
    """
    # Ensure collection_names is a list, even if a single name is provided
    if isinstance(collection_names, str):
        collection_names = [collection_names]

    print(f"Resetting rotations for bones in collections: {collection_names}...")

    # Iterate through the provided collection names
    for collection_name in collection_names:
        # Access bone collections from armature.data
        bone_collection = armature.data.collections_all.get(collection_name)
        if not bone_collection:
            print(f"Bone collection '{collection_name}' not found. Skipping.")
            continue
        
        # Check if the collection is visible (optional, you may not need this)
        if not bone_collection.is_visible:
            print(f"Bone collection '{collection_name}' is hidden. Unhiding for processing.")
            bone_collection.is_visible = True

        # Iterate through all bones in the specified collection
        for bone in bone_collection.bones:
            pose_bone = armature.pose.bones.get(bone.name)
            if pose_bone:
                # Check if the pose bone has any of the specified constraints
                has_valid_constraint = any(
                    constraint.type in {'COPY_ROTATION', 'COPY_LOCATION', 'COPY_TRANSFORMS'}
                    for constraint in pose_bone.constraints
                )
                
                if has_valid_constraint:
                    print(f"Resetting rotation for bone '{pose_bone.name}' in collection '{collection_name}'...")
                    pose_bone.rotation_quaternion = Quaternion((1, 0, 0, 0))
    
    print("Rotation reset completed.")

def load_bone(bone, path, diff):
    #Load a single bone from the current .pose file to the current armature
    bone: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    diff: bpy.props.FloatVectorProperty(size=4)
    
    context = bpy.context
    arm = context.object.pose

    with open(path, 'r') as f:
        pose = json.load(f)['Bones']
        
    bone = arm.bones[bone]
    if not bone:
        print(f"Bone '{bone}' not found.")
        return {'FINISHED'}

    trans = pose.get(bone)
    if not trans:
        print(f"Bone '{bone}' not found in the pose file.")
        return {'FINISHED'}

    # Apply rotation
    rot = trans["Rotation"].split(", ")
    rot = [float(x) for x in rot]
    # Convert XYZW to WXYZ
    rot.insert(0, rot.pop())
    diff_quat = Quaternion(diff[:3], diff[3])
    rot = Quaternion(rot) @ diff_quat
    bone.rotation_quaternion = context.object.convert_space(
        pose_bone=bone,
        matrix=rot.to_matrix().to_4x4(),
        from_space='POSE',
        to_space='LOCAL'
    ).to_quaternion()
    
def import_pose(filepath, armature):
    print("Starting pose import process...")
    
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
        #bpy.ops.pose.load_bone('EXEC_DEFAULT', bone=bone.name, path=filepath, diff=diff)
        load_bone(bone.name, filepath, diff)
        
    # Reverse constraints
    reverse_constraints(armature)
    
    #Pole target Calculation and Adjustment
    set_pole_targets(armature)

    # Re-enable constraints
    for bone in arm.bones:
        for constraint in bone.constraints:
            constraint.mute = False
                   
    reset_bones_in_collections(armature, ["Base Bones", "DT Face Bones"])
            
    # Reset root bone rotation
    root_bone.rotation_quaternion = Quaternion([1, 0, 0, 0])
    print("Pose import completed successfully.")
    return {'FINISHED'}
    
class IMPORT_POSE_OT(bpy.types.Operator):
    bl_idname = "import_pose.file"
    bl_label = "Import Pose File"
    arg: bpy.props.StringProperty()

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # Ensure an armature is selected
        armature = context.object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected.")
            return {'CANCELLED'}

        # Import the pose
        import_pose(self.filepath, armature)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(IMPORT_POSE_OT)

def unregister():
    bpy.utils.unregister_class(IMPORT_POSE_OT)
