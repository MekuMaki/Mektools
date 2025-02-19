import bpy
import mathutils
import math

def generatr_tail_spline_ik(armature, reference_bone_names, curve_name):
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create the standard IK bone chain with slight hyperbolic offset
    bpy.ops.object.mode_set(mode='EDIT')
    ik_bones_names = []
    pole_target_offset = mathutils.Vector((0, -0.005, 0))
    for index, bone_name in enumerate(reference_bone_names[:-1]):  # Exclude last reference from IK chain creation
        ik_bone = armature.data.edit_bones.new(f"IK_bone_{bone_name}")
        ik_bone.head = armature.data.edit_bones[bone_name].head
        if index < len(reference_bone_names) - 2:  # Prevent out of range index for the last bone
            next_bone_name = reference_bone_names[index + 1]
            ik_bone.tail = armature.data.edit_bones[next_bone_name].head
        else:
            # Set the tail of the last bone using the last reference bone's head
            ik_bone.tail = armature.data.edit_bones[reference_bone_names[-1]].head

        ik_bone.tail += pole_target_offset * (1 - ((len(reference_bone_names) - 1 - index) / (len(reference_bone_names) - 1)) ** 2)
        if index > 0:
            ik_bone.parent = armature.data.edit_bones[ik_bones_names[-1]]
            ik_bone.use_connect = True
        ik_bones_names.append(ik_bone.name)

    # Create IK target and pole target
    ik_target_bone = armature.data.edit_bones.new("IK_Target_Tail")
    ik_target_bone.head = armature.data.edit_bones[reference_bone_names[-1]].head
    ik_target_bone.tail = ik_target_bone.head + mathutils.Vector((0, 0.1, 0))

    pole_target_bone = armature.data.edit_bones.new("Pole_Target_Tail")
    pole_target_bone.head = armature.data.edit_bones[reference_bone_names[2]].head + mathutils.Vector((0, 0.3, 0))
    pole_target_bone.tail = pole_target_bone.head + mathutils.Vector((0, 0.1, 0))

    bpy.ops.object.mode_set(mode='POSE')

    # Apply IK constraints
    # Apply IK constraint to the second-to-last IK bone
    if len(ik_bones_names) > 1:
        second_last_ik_bone_name = ik_bones_names[-1]
        second_last_ik_bone = armature.pose.bones[second_last_ik_bone_name]
        ik_constraint = second_last_ik_bone.constraints.new('IK')
        ik_constraint.target = armature
        ik_constraint.subtarget = "IK_Target_Tail"
        ik_constraint.pole_target = armature
        ik_constraint.pole_subtarget = "Pole_Target_Tail"
        ik_constraint.chain_count = len(ik_bones_names)
        ik_constraint.pole_angle = math.radians(90)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Create control bones and ensure the last one parents to the IK target
    bpy.ops.object.mode_set(mode='EDIT')
    for index, bone_name in enumerate(reference_bone_names):
        ctrl_bone_name = f"SplineCtrl_bone_{bone_name}"
        ctrl_bone = armature.data.edit_bones.new(ctrl_bone_name)
        ref_bone = armature.data.edit_bones[bone_name]
        ctrl_bone.head = ref_bone.head
        ctrl_bone.tail = ref_bone.tail
        if index == len(reference_bone_names) - 1:
            # Last control bone parents to IK target
            ctrl_bone.parent = armature.data.edit_bones["IK_Target_Tail"]
        else:
            # Other control bones parent to their corresponding IK bones
            ctrl_bone.parent = armature.data.edit_bones[ik_bones_names[index]]

    bpy.ops.object.mode_set(mode='OBJECT')

    curve_data = bpy.data.curves.new(name=curve_name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_object = bpy.data.objects.new(curve_name, curve_data)
    bpy.context.collection.objects.link(curve_object)

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(reference_bone_names) - 1)

    for i, bone_name in enumerate(reference_bone_names):
        bone = armature.data.bones[bone_name]
        bp = spline.bezier_points[i]
        bp.co = armature.matrix_world @ bone.head_local
        bp.handle_left_type = bp.handle_right_type = 'AUTO'

    bpy.ops.object.mode_set(mode='OBJECT')

    # Setup hooks and ensure they are assigned
    bpy.context.view_layer.objects.active = curve_object
    bpy.ops.object.mode_set(mode='OBJECT')

    for i, bone_name in enumerate(reference_bone_names):
        control_bone_name = f"SplineCtrl_bone_{bone_name}"
        hook_modifier = curve_object.modifiers.new(name=f"Hook_{control_bone_name}", type='HOOK')
        hook_modifier.object = armature
        hook_modifier.subtarget = control_bone_name

         # Assign each vertex to the hook
        bpy.ops.object.mode_set(mode='EDIT')
        if i < len(curve_object.data.splines[0].bezier_points):  # Check to ensure index is within range
            curve_object.data.splines[0].bezier_points[i].select_control_point = True
            bpy.ops.object.hook_assign(modifier=hook_modifier.name)
            bpy.ops.curve.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

    print("Hooks assigned successfully.")
    
    
    
        # Create the IK bone chain with correct tail direction
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    spl_ik_bones_names = []
    prev_spl_ik_bone = None  # Initialize variable for previous IK bone
    for index, spl_bone_name in enumerate(reference_bone_names):
        spl_ik_bone = armature.data.edit_bones.new(f"SplineIK_bone_{spl_bone_name}")
        spl_ik_bone.head = armature.data.edit_bones[spl_bone_name].head
        if index < len(reference_bone_names) - 1:
            next_spl_bone_name = reference_bone_names[index + 1]
            spl_ik_bone.tail = armature.data.edit_bones[next_spl_bone_name].head
        else:
            spl_ik_bone.tail = spl_ik_bone.head
        if prev_spl_ik_bone:
            spl_ik_bone.parent = prev_spl_ik_bone  # Set the parent to the previous IK bone
            spl_ik_bone.use_connect = True     # Ensure the bones are connected
        else:
            spl_ik_bone.parent = None  # First bone does not have a parent

        prev_spl_ik_bone = spl_ik_bone  # Update the previous IK bone
        spl_ik_bones_names.append(spl_ik_bone.name)  # Store the names for later reference

    bpy.ops.object.mode_set(mode='OBJECT')

    # Apply Spline IK constraint to the last IK bone created
    bpy.ops.object.mode_set(mode='POSE')
    if spl_ik_bones_names:  # Check if list is not empty
        last_spl_ik_bone_name = spl_ik_bones_names[-2]  # Safely access the last bone name
        last_spl_ik_bone = armature.pose.bones[last_spl_ik_bone_name]  # Access PoseBone for constraints
        spline_ik = last_spl_ik_bone.constraints.new('SPLINE_IK')
        spline_ik.target = curve_object
        spline_ik.chain_count = len(spl_ik_bones_names)  # Use the number of IK bones
         # Set the Spline IK specific settings
        spline_ik.use_even_divisions = True  # Fitting: Even Division
        spline_ik.y_scale_mode = 'BONE_ORIGINAL'  # Y Scale Mode: Bone Original
        spline_ik.xz_scale_mode = 'BONE_ORIGINAL'  # XZ Scale Mode: Bone Original

    bpy.ops.object.mode_set(mode='OBJECT')
    print("IK chain and Spline IK setup completed.")
    
    
    
    
    
    bpy.ops.object.mode_set(mode='POSE')

    # Apply Copy Rotation constraints to each reference bone except the last
    for i in range(len(reference_bone_names) - 1):  # Exclude the last reference bone
        ref_bone = armature.pose.bones[reference_bone_names[i]]
        spl_ik_bone_name = f"SplineIK_bone_{reference_bone_names[i]}"
        
        copy_rot = ref_bone.constraints.new('COPY_ROTATION')
        copy_rot.target = armature
        copy_rot.subtarget = spl_ik_bone_name
        copy_rot.target_space = 'LOCAL_OWNER_ORIENT'
        copy_rot.owner_space = 'LOCAL'
        copy_rot.mix_mode = 'AFTER'
        copy_rot.use_x = True
        copy_rot.use_y = True
        copy_rot.use_z = True
        copy_rot.use_offset = False
        copy_rot.euler_order = 'ZXY'
        
        
        # Special case: last reference bone's Copy Rotation constraint targets the IK Target
    last_ref_bone = armature.pose.bones[reference_bone_names[-1]]
    last_copy_rot = last_ref_bone.constraints.new('COPY_ROTATION')
    last_copy_rot.target = armature
    last_copy_rot.subtarget = "IK_Target_Tail"  # Assuming the IK target bone's name is set
    last_copy_rot.target_space = 'LOCAL_OWNER_ORIENT'
    last_copy_rot.owner_space = 'LOCAL'
    last_copy_rot.mix_mode = 'AFTER'
    last_copy_rot.use_x = True
    last_copy_rot.use_y = True
    last_copy_rot.use_z = True
    last_copy_rot.use_offset = False
    last_copy_rot.euler_order = 'ZXY'

    bpy.ops.object.mode_set(mode='OBJECT')
    print("Copy Rotation constraints applied successfully.")
    
    
    
    
    

    print("Standard IK chain and Spline IK setup completed.")