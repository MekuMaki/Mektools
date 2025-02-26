import bpy
from ..libs import helper
  
class MEKTOOLS_OT_ACTORS_RefreshActors(bpy.types.Operator):
    """Refresh the list of actors and categorize them"""
    bl_idname = "mektools.ot_refresh_actors"
    bl_label = "Refresh Actors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.actors.clear()

        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.data: 
                actor = scene.actors.add()
                actor.armature = obj

        return {'FINISHED'}
   
class MEKTOOLS_OT_ToggleHideNonActors(bpy.types.Operator):
    """Toggle hiding non-actor armatures in the UI list"""
    bl_idname = "mektools.ot_toggle_hide_non_actors"
    bl_label = "Toggle Hide Non-Actors"

    def execute(self, context):
        scene = context.scene
        scene.hide_non_actors = not scene.hide_non_actors
        return {'FINISHED'}
    
class MEKTOOLS_OT_ToggleActorVisibility(bpy.types.Operator):
    """Toggles visibility for an actor's armature and parented objects"""
    bl_idname = "mektools.ot_toggle_actor_visibility"
    bl_label = "Toggle Actor Visibility"
    
    armature_name: bpy.props.StringProperty()
    hide_armature: bpy.props.BoolProperty(default=False)
    hide_actor: bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        scene = context.scene
        armature = bpy.data.objects.get(self.armature_name)

        if not armature:
            return {'CANCELLED'}

        actor_item = next((a for a in scene.actors if a.armature == armature), None)

        if actor_item is None:
            return {'CANCELLED'}
         
        actor_item.armature.data["mektools_actor_hide_armature"] = self.hide_armature
        actor_item.armature.data["mektools_actor_hide_actor"] = self.hide_actor
        

        # Ensure actor armature is hidden if actor is hidden
        if self.hide_actor:
            self.hide_armature = True

        # Toggle armature visibility
        helper.safe_hide_set(context, armature, self.hide_armature)

        # Toggle actor visibility (all parented objects)
        for child in armature.children:
            helper.safe_hide_set(context, child, self.hide_actor)

        return {'FINISHED'}
    
    
class MEKTOOLS_OT_Set_Is_Actor(bpy.types.Operator):
    """Toggle hiding non-actor armatures in the UI list"""
    bl_idname = "mektools.ot_set_is_actor"
    bl_label = "Set is_actor property of armature"

    is_actor: bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        scene = context.scene
        if len(scene.actors) > 0 and 0 <= scene.actors_index < len(scene.actors):
            actor = scene.actors[scene.actors_index]
            if actor.armature:
                actor.armature.data["mektools_is_actor"] = self.is_actor
        
        
        return {'FINISHED'}
    
class MEKTOOLS_OT_RenameActor(bpy.types.Operator):
    """Rename the active actor with a unique name"""
    bl_idname = "mektools.ot_rename_actor"
    bl_label = "Rename Actor"
    bl_options = {'REGISTER', 'UNDO'}

    new_name: bpy.props.StringProperty(name="New Name")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        scene = context.scene
        actor = scene.actors[scene.actors_index]
        
        if not actor:
            self.report({'WARNING'}, "No valid actor selected.")
            return {'CANCELLED'}
        
        # Rename the actor
        actor.armature.name= self.new_name
        self.report({'INFO'}, f"Renamed to {self.new_name}")
        return {'FINISHED'}
    
    
class MEKTOOLS_OT_DuplicateActor(bpy.types.Operator):
    """Duplicate the active actor"""
    bl_idname = "mektools.ot_duplicate_actor"
    bl_label = "Duplicate Actor"
    bl_options = {'REGISTER', 'UNDO'}

    duplicate_with_parent: bpy.props.BoolProperty(name="Duplicate Parent Collection", default=False)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        scene = context.scene
        actor = scene.actors[scene.actors_index]
        
        if not actor:
            self.report({'WARNING'}, "No valid actor selected.")
            return {'CANCELLED'}
        
        if self.duplicate_with_parent and actor.armature.users_collection:
            collection = actor.armature.users_collection[0]
            new_collection = helper.create_collection(collection.name)
            
            helper.dupe_with_childs(actor.armature)
            
            for obj in context.selected_objects:
                collection.objects.unlink(obj)
                new_collection.objects.link(obj)

        else:
            helper.dupe_with_childs(actor.armature)
        
        bpy.ops.mektools.ot_refresh_actors()
        self.report({'INFO'}, "Actor duplicated successfully")
        return {'FINISHED'}
    
class MEKTOOLS_OT_DeleteActor(bpy.types.Operator):
    """Delete the active actor"""
    bl_idname = "mektools.ot_delete_actor"
    bl_label = "Delete Actor"
    bl_options = {'REGISTER', 'UNDO'}

    delete_parent_collection: bpy.props.BoolProperty(name="Delete Parent Collection", default=False)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        scene = context.scene
        actor = scene.actors[scene.actors_index]
        
        if not actor:
            self.report({'WARNING'}, "No valid actor selected.")
            return {'CANCELLED'}
        
        armature = actor.armature
        
        if self.delete_parent_collection and armature.users_collection:
            collection = armature.users_collection[0]
            
            # Unlink and remove all objects in the collection
            for obj in list(collection.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            
            # Remove the collection itself
            bpy.data.collections.remove(collection)
        else:
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            
            # Select and delete all children
            for child in list(armature.children):
                child.select_set(True)
                bpy.data.objects.remove(child, do_unlink=True)
            
            bpy.ops.object.delete()
        
        # Remove actor from the actor list
        scene.actors.remove(scene.actors_index)
        
        # Ensure orphaned data is cleaned
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        
        bpy.ops.mektools.ot_refresh_actors()
        self.report({'INFO'}, "Actor and all associated data deleted successfully.")
        return {'FINISHED'}
    
    
def register():
    bpy.utils.register_class(MEKTOOLS_OT_DuplicateActor)
    bpy.utils.register_class(MEKTOOLS_OT_RenameActor)
    bpy.utils.register_class(MEKTOOLS_OT_ToggleActorVisibility)
    bpy.utils.register_class(MEKTOOLS_OT_Set_Is_Actor)
    bpy.utils.register_class(MEKTOOLS_OT_ToggleHideNonActors)
    bpy.utils.register_class(MEKTOOLS_OT_DeleteActor)
    bpy.utils.register_class(MEKTOOLS_OT_ACTORS_RefreshActors)
    
    bpy.types.Scene.hide_non_actors = bpy.props.BoolProperty(name="Hide Non-Actors", default=False)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_DuplicateActor)
    bpy.utils.unregister_class(MEKTOOLS_OT_RenameActor)
    bpy.utils.unregister_class(MEKTOOLS_OT_ToggleActorVisibility)
    bpy.utils.unregister_class(MEKTOOLS_OT_Set_Is_Actor)
    bpy.utils.unregister_class(MEKTOOLS_OT_ToggleHideNonActors)
    bpy.utils.unregister_class(MEKTOOLS_OT_DeleteActor)
    bpy.utils.unregister_class(MEKTOOLS_OT_ACTORS_RefreshActors)