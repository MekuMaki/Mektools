import bpy
from ..libs import helper, pins
     
class MEKTOOLS_OT_TogglePinVisibility(bpy.types.Operator):
    """Toggles visibility for a pin and parented objects"""
    bl_idname = "mektools.ot_toggle_pin_visibility"
    bl_label = "Toggle Pin Visibility"
    
    object_name: bpy.props.StringProperty()
    hide_armature: bpy.props.BoolProperty(default=False)
    hide_object: bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        obj = bpy.data.objects.get(self.object_name)

        if not obj:
            return {'CANCELLED'}
         
        obj.data["mt_actor_hide_armature"] = self.hide_armature
        obj.data["mt_actor_hide_object"] = self.hide_object
        

        # Ensure pins armature is hidden if pin is hidden
        if self.hide_object:
            self.hide_armature = True

        # Toggle armature visibility
        if obj.type == "ARMATURE":
            helper.safe_hide_set(context, obj, self.hide_armature)

        # Toggle pin visibility (all parented objects)
        for child in obj.children:
            helper.safe_hide_set(context, child, self.hide_object)

        return {'FINISHED'}
    
    
    
class MEKTOOLS_OT_DuplicatePin(bpy.types.Operator):
    """Duplicate the active Pin"""
    bl_idname = "mektools.ot_duplicate_pin"
    bl_label = "Duplicate Pin"
    bl_options = {'REGISTER', 'UNDO'}

    duplicate_with_parent: bpy.props.BoolProperty(name="Duplicate Parent Collection", default=False)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        pins.remove_callback()
        scene = context.scene
        pin = scene.pins[scene.pins_index]
        
        if not pin:
            self.report({'WARNING'}, "No valid Pin selected.")
            return {'CANCELLED'}
        
        obj = pin.object
        
        if self.duplicate_with_parent and obj.users_collection:
            collection = obj.users_collection[0]
            new_collection = helper.create_collection(collection.name)
            
            helper.dupe_with_childs(obj)
            
            for obj in context.selected_objects:
                collection.objects.unlink(obj)
                new_collection.objects.link(obj)

        else:
            helper.dupe_with_childs(obj)
            
        pins.sync_list_with_viewport_selection(scene)
        
        pins.add_callback()
        
        self.report({'INFO'}, "Actor duplicated successfully")
        return {'FINISHED'}
    
class MEKTOOLS_OT_DeletePin(bpy.types.Operator):
    """Delete the active Pin"""
    bl_idname = "mektools.ot_delete_pin"
    bl_label = "Delete Pin"
    bl_options = {'REGISTER', 'UNDO'}

    delete_parent_collection: bpy.props.BoolProperty(name="Delete Parent Collection", default=False)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        scene = context.scene
        pin = scene.pins[scene.pins_index]
        
        if not pin:
            self.report({'WARNING'}, "No valid Pin selected.")
            return {'CANCELLED'}
        
        obj = pin.object
        
        if self.delete_parent_collection and obj.users_collection:
            collection = obj.users_collection[0]
            
            # Unlink and remove all objects in the collection
            for obj in list(collection.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            
            # Remove the collection itself
            bpy.data.collections.remove(collection)
        else:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            
            # Select and delete all children
            for child in list(obj.children):
                child.select_set(True)
                bpy.data.objects.remove(child, do_unlink=True)
            
            bpy.ops.object.delete()
        
        # Remove pin from the pin list
        scene.pins.remove(scene.pins_index)
        
        self.report({'INFO'}, "Pin and all associated data deleted successfully.")
        return {'FINISHED'}
    
class MEKTOOLS_OT_SetIsPinned(bpy.types.Operator):
    bl_idname = "mektools.set_is_pinned"
    bl_label = "Toggle Pin Object"
    bl_description = "Add or remove the active object from the pin list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        obj = context.active_object

        if not obj:
            self.report({'ERROR'}, "No active object to pin/unpin")
            return {'CANCELLED'}

        # Check if object is already pinned
        pins_index = next((i for i, item in enumerate(scene.pins) if item.object == obj), -1)

        if pins_index >= 0:
            # Object is pinned, remove it
            scene.pins.remove(pins_index)
            self.report({'INFO'}, f"Unpinned: {obj.name}")
        else:
            # Object is NOT pinned, so we add it
            pin = scene.pins.add()
            pin.object = obj
            self.report({'INFO'}, f"Pinned: {obj.name}")

        return {'FINISHED'}
    
    
def register():
    bpy.utils.register_class(MEKTOOLS_OT_DuplicatePin)
    bpy.utils.register_class(MEKTOOLS_OT_TogglePinVisibility)
    bpy.utils.register_class(MEKTOOLS_OT_DeletePin)
    bpy.utils.register_class(MEKTOOLS_OT_SetIsPinned)
    
    bpy.app.handlers.depsgraph_update_post.append(pins.on_update_callback)
    bpy.types.Scene.hide_non_pins = bpy.props.BoolProperty(name="Hide Non-pins", default=False)

def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(pins.on_update_callback)
    
    bpy.utils.unregister_class(MEKTOOLS_OT_DuplicatePin)
    bpy.utils.unregister_class(MEKTOOLS_OT_TogglePinVisibility)
    bpy.utils.unregister_class(MEKTOOLS_OT_DeletePin)
    bpy.utils.unregister_class(MEKTOOLS_OT_SetIsPinned)