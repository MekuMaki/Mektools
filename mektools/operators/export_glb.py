import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

class EXPORT_ACTION_OT_glb(Operator, ExportHelper):
    bl_idname = "export_action.glb"
    bl_label = "Export Animation"
    arg: bpy.props.StringProperty()

    filename_ext = ".glb"
    filter_glob: StringProperty(default="*.glb", options={'HIDDEN'})

    post_dialog: BoolProperty(default=False)  # Flag to control if export helper should open next

    # Enum property for selecting an action
    action_name: EnumProperty(
        name="Action",
        description="Select an action to export",
        items=lambda self, context: [(action.name, action.name, "") for action in bpy.data.actions]
    )
    
    @classmethod
    def description(cls, context, properties):
        return properties.arg

    def invoke(self, context, event):
        actions = bpy.data.actions
        if len(actions) == 1:
            # If only one action exists, select it automatically and open export helper
            self.action_name = actions[0].name
            self.filepath = bpy.path.abspath(f"//{self.action_name}.glb")
            self.post_dialog = True
            return ExportHelper.invoke(self, context, event)
        else:
            # Show the dropdown for action selection
            self.post_dialog = False
            return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "action_name", text="Select Action")

    def execute(self, context):
        if not self.post_dialog:
            # Set the flag to open the export helper next and return to invoke it
            self.post_dialog = True
            self.filepath = bpy.path.abspath(f"//{self.action_name}.glb")
            return ExportHelper.invoke(self, context, None)
        else:
            # Reset flag and proceed with the actual export
            self.post_dialog = False

            # Set the active action to the selected one
            action = bpy.data.actions.get(self.action_name)
            if action:
                context.object.animation_data.action = action
            else:
                self.report({'ERROR'}, "Action not found.")
                return {'CANCELLED'}

            # Perform the actual export with custom settings
            bpy.ops.export_scene.gltf(
                filepath=self.filepath,
                export_format='GLB',
                use_selection=True,
                export_yup=True,
                export_apply=True,
                export_animations=True,
                export_frame_range=True,
                export_anim_slide_to_zero=True,
                export_animation_mode='ACTIVE_ACTIONS',
                export_optimize_animation_size=False,
                export_optimize_animation_keep_anim_armature=True,
                export_optimize_animation_keep_anim_object=True,
                export_materials='NONE'
            )
            self.report({'INFO'}, f"GLB exported to {self.filepath}")
            return {'FINISHED'}
    
class EXPORT_VFXOBJ_OT_glb(Operator, ExportHelper):
    bl_idname = "export_vfxobj.glb"
    bl_label = "Export Model"
    arg: bpy.props.StringProperty()
    filename_ext = ".glb"
    filter_glob: StringProperty(default="*.glb", options={'HIDDEN'})
    
    @classmethod
    def description(cls, context, properties):
        return properties.arg

    def invoke(self, context, event):
        self.filepath = bpy.path.abspath(f"//vfxobj.glb")
        return ExportHelper.invoke(self, context, event)
            
    def execute(self, context):
        filepath = self.filepath if self.filepath else bpy.path.abspath("//vfxobj.glb")

        # Custom export settings
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format='GLB',
            use_selection=True,
            export_texcoords=True,
            export_normals=True, 
            export_tangents=True, 
            export_yup=True,  # Apply Y-up coordinate system
            export_apply=True,  # Apply modifiers
            export_materials='NONE'  # No material export needed
        )

        self.report({'INFO'}, f"GLB exported to {filepath}")
        return {'FINISHED'}

# Register and unregister the operator
def register():
    bpy.utils.register_class(EXPORT_ACTION_OT_glb)
    bpy.utils.register_class(EXPORT_VFXOBJ_OT_glb)

def unregister():
    bpy.utils.unregister_class(EXPORT_ACTION_OT_glb)
    bpy.utils.unregister_class(EXPORT_VFXOBJ_OT_glb)