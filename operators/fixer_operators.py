import bpy

class OBJECT_OT_fix_backface_culling(bpy.types.Operator):
    """Disable Backface Culling for All Materials"""
    bl_idname = "object.fix_backface_culling"
    bl_label = "Fix Backface Culling"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for material in bpy.data.materials:
            material.use_backface_culling = False
        self.report({'INFO'}, "Backface Culling disabled for all materials.")
        return {'FINISHED'}


class MESH_OT_clear_custom_split_normals(bpy.types.Operator):
    """Clear Custom Split Normals for Selected Mesh"""
    bl_idname = "mesh.clear_custom_split_normals"
    bl_label = "Clear Custom Split Normals"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Apply to all selected mesh objects
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
        self.report({'INFO'}, "Custom Split Normals cleared for selected mesh.")
        return {'FINISHED'}

class MEKTOOLS_OT_ClearParents (bpy.types.Operator):
    """Clear Parent Keep Transforms on selected objects"""
    bl_idname = "mektools.clear_parents"
    bl_label = "Clear Parents (Keep Transforms)"
    bl_options = {'REGISTER', 'UNDO'}    

    def execute(self, context):
        # Run Blender's internal Clear Parent Keep Transform operation
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        self.report({'INFO'}, "Cleared parents and kept transforms for selected objects.")
        return {'FINISHED'}

# Register and unregister classes
def register():
    bpy.utils.register_class(OBJECT_OT_fix_backface_culling)
    bpy.utils.register_class(MESH_OT_clear_custom_split_normals)
    bpy.utils.register_class(MEKTOOLS_OT_ClearParents)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_fix_backface_culling)
    bpy.utils.unregister_class(MESH_OT_clear_custom_split_normals)
    bpy.utils.unregister_class(MEKTOOLS_OT_ClearParents)
