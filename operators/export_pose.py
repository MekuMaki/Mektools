import bpy
import json
import os
import re
from bpy.types import Operator
from bpy.props import BoolProperty
from bpy_extras.io_utils import ExportHelper  
from ..preferences.pose_preferences import PosePreferences 

BONE_GROUPS = ["Hair", "Face", "HandL", "HandR", "Tail", "Gear", "Body"]

class EXPORT_POSE_OT(Operator, ExportHelper):
    """Exports armature pose into a .pose file."""
    bl_idname = "pose.export"
    bl_label = "Export to Pose File"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext = '.pose'
    filter_glob: bpy.props.StringProperty(default='*.pose', options={'HIDDEN'})
    
    # Create properties for bone group selection with default as True
    for group in BONE_GROUPS:
        exec(f"{group}: BoolProperty(name=\"{group}\", default=True)")
    
    # Properties for selecting what to save
    save_position: BoolProperty(name="Pos", default=True)
    save_rotation: BoolProperty(name="Rot", default=True)
    save_scale: BoolProperty(name="Scale", default=True)
    
    
    def invoke(self, context, event):
        prefs = context.preferences.addons["Mektools"].preferences  # Access the preferences
        blend_filename = bpy.path.basename(bpy.data.filepath)  # Get the Blender file name
        if blend_filename:
            blend_filename = os.path.splitext(blend_filename)[0] + ".pose"  # Change extension to .pose
        else:
            blend_filename = "untitled.pose"  # Fallback if the file hasn't been saved
        
        if prefs.default_pose_export_path:
            self.filepath = os.path.join(prefs.default_pose_export_path, blend_filename)
        else:
            self.filepath = blend_filename
        
        return super().invoke(context, event)
    
    
    def draw(self, context):
        layout = self.layout

        layout.label(text="Select Properties to Save:")
      
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "save_position", toggle=False)
        row.prop(self, "save_rotation", toggle=False)
        row.prop(self, "save_scale", toggle=False)

        layout.separator()
      
        layout.label(text="Select Bone Groups to Export:")
      
        col = layout.column(align=True)
        col.prop(self, "Hair", toggle=True)
        col.prop(self, "Face", toggle=True) 
      
        row = col.row(align=True)
        row.prop(self, "HandL", toggle=True)
        row.prop(self, "HandR", toggle=True)
      
        col.prop(self, "Tail", toggle=True)
        col.prop(self, "Gear", toggle=True)
        col.prop(self, "Body", toggle=True)
        
        

    
    def execute(self, context):
        # Load bone groups from the JSON file
        json_path = os.path.join(os.path.dirname(__file__), "..", "data", "bone_groups.json")
        with open(json_path) as f:
            bone_groups = json.load(f)
        
        # Get selected bone groups from the export dialog
        selected_groups = {group for group in BONE_GROUPS if getattr(self, group)}
        selected_bones = [bone for group in selected_groups for bone in bone_groups.get(group, [])]
        
        if "Hair" in selected_groups:
            selected_bones.extend([bone.name for bone in context.object.pose.bones if bone.name.startswith("j_ex")])
        
        # Prepare data for export
        armature = context.object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "No armature selected")
            return {'CANCELLED'}
        
        root_bone = armature.pose.bones.get("n_throw")
        if not root_bone:
            self.report({'ERROR'}, "Origin bone 'n_throw' not found")
            return {'CANCELLED'}
        
        root_matrix_world = armature.matrix_world @ root_bone.matrix
        skeleton_data = {
            "FileExtension": ".pose",
            "TypeName": "Mektools Pose",
            "FileVersion": 2,
            "Bones": {}
        }
        
        # Collect data for selected bones
        for bone_name in selected_bones:
            clean_bone_name = re.sub(r"\.\d+$", "", bone_name)  # Remove .xxx suffix
            bone = armature.pose.bones.get(bone_name)
            if bone:
                bone_matrix_world = armature.matrix_world @ bone.matrix
                relative_matrix = root_matrix_world.inverted() @ bone_matrix_world
                
                bone_data = {}
                if self.save_position:
                    bone_data["Position"] = f"{relative_matrix.translation.x:.6f}, {relative_matrix.translation.y:.6f}, {relative_matrix.translation.z:.6f}"
                if self.save_rotation:
                    bone_data["Rotation"] = f"{relative_matrix.to_quaternion().x:.6f}, {relative_matrix.to_quaternion().y:.6f}, {relative_matrix.to_quaternion().z:.6f}, {relative_matrix.to_quaternion().w:.6f}"
                if self.save_scale:
                    bone_data["Scale"] = f"{relative_matrix.to_scale().x:.8f}, {relative_matrix.to_scale().y:.8f}, {relative_matrix.to_scale().z:.8f}"
                
                skeleton_data["Bones"][clean_bone_name] = bone_data
        
        # Write to the file
        with open(self.filepath, 'w') as f:
            json.dump(skeleton_data, f, indent=4)
        
        self.report({'INFO'}, "Pose exported successfully!")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(EXPORT_POSE_OT)

def unregister():
    bpy.utils.unregister_class(EXPORT_POSE_OT)

