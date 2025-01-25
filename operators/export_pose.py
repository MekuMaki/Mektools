import bpy
import json
import os
from bpy.types import Operator
from bpy.props import BoolProperty
from bpy_extras.io_utils import ExportHelper  

BONE_GROUPS = ["Hair", "Face", "HandL", "HandR", "Tail", "Gear", "Body"]

class EXPORT_SKELETON_OT_pose(Operator, ExportHelper):
    bl_idname = "export_skeleton.pose"
    bl_label = "Export Skeleton Pose"
    arg: bpy.props.StringProperty()
    
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext='.pose'
    filter_glob: bpy.props.StringProperty(
        default='*.pose',
        options={'HIDDEN'}
    )

    @classmethod
    def description(cls, context, properties):
        return properties.arg
    
    def execute(self, context):
        # Load bone groups from the JSON file
        json_path = os.path.join(os.path.dirname(__file__), "..", "data", "bone_groups.json")
        with open(json_path) as f:
            bone_groups = json.load(f)

        # Get selected groups based on the panel selections
        bone_group_props = context.scene.bone_group_props
        selected_groups = {name for name in BONE_GROUPS if getattr(bone_group_props, name)}
        selected_bones = [bone for group in selected_groups for bone in bone_groups.get(group, [])]
        
        for group in selected_groups:
            selected_bones.extend(bone_groups.get(group, []))

            # If the 'Hair' group is selected, include all bones that start with 'j_ex'
            if group == "Hair":
                selected_bones.extend([bone.name for bone in context.object.pose.bones if bone.name.startswith("j_ex")])
        
        # Prepare data for export
        armature = context.object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected")
            return {'CANCELLED'}
        
        # Origin bone assumed as "n_throw"
        root_bone = armature.pose.bones.get("n_throw")
        if not root_bone:
            self.report({'ERROR'}, "Origin bone 'n_throw' not found")
            return {'CANCELLED'}
        
        root_matrix_world = armature.matrix_world @ root_bone.matrix
        skeleton_data = {
            "FileExtension": ".pose",
            "TypeName": "Ktisis Pose",
            "FileVersion": 2,
            "Position": f"{root_matrix_world.translation.x:.6f}, {root_matrix_world.translation.y:.6f}, {root_matrix_world.translation.z:.6f}",
            "Rotation": f"{root_matrix_world.to_quaternion().x:.6f}, {root_matrix_world.to_quaternion().y:.6f}, {root_matrix_world.to_quaternion().z:.6f}, {root_matrix_world.to_quaternion().w:.6f}",
            "Scale": f"{root_matrix_world.to_scale().x:.6f}, {root_matrix_world.to_scale().y:.6f}, {root_matrix_world.to_scale().z:.6f}",
            "Bones": {}
        }

        # Collect data for selected bones
        for bone_name in selected_bones:
            bone = armature.pose.bones.get(bone_name)
            if bone:
                bone_matrix_world = armature.matrix_world @ bone.matrix
                relative_matrix = root_matrix_world.inverted() @ bone_matrix_world

                bone_data = {
                    "Position": f"{relative_matrix.translation.x:.6f}, {relative_matrix.translation.y:.6f}, {relative_matrix.translation.z:.6f}",
                    "Rotation": f"{relative_matrix.to_quaternion().x:.6f}, {relative_matrix.to_quaternion().y:.6f}, {relative_matrix.to_quaternion().z:.6f}, {relative_matrix.to_quaternion().w:.6f}",
                    "Scale": f"{relative_matrix.to_scale().x:.8f}, {relative_matrix.to_scale().y:.8f}, {relative_matrix.to_scale().z:.8f}"
                }
                skeleton_data["Bones"][bone_name] = bone_data
        
        # Write to the file
        with open(self.filepath, 'w') as f:
            json.dump(skeleton_data, f, indent=4)

        self.report({'INFO'}, "Pose exported successfully!")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(EXPORT_SKELETON_OT_pose)

def unregister():
    bpy.utils.unregister_class(EXPORT_SKELETON_OT_pose)