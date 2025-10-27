import bpy
import os

class MEKTOOLS_OT_append_projection_plane(bpy.types.Operator):
    bl_idname = "mektools.append_projection_plane"
    bl_label = "Projection Plane"
    bl_description = "Appends a Orthogonal Projection Plane"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        blend_path = os.path.join(os.path.dirname(__file__), "..", "assets", "opp.blend")
        object_name = "Orthogonal Projection Plane"

        # Append the object from the blend file
        with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
            if object_name in data_from.objects:
                data_to.objects.append(object_name)

        if data_to.objects:
            obj = data_to.objects[0]
            bpy.context.collection.objects.link(obj)
            obj.location = bpy.context.scene.cursor.location

        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(MEKTOOLS_OT_append_projection_plane)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_append_projection_plane)

