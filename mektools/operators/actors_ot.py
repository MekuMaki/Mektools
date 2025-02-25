import bpy
from ..libs import actors
  
class MEKTOOLS_OT_ACTORS_RefreshActors(bpy.types.Operator):
    """Refresh the list of actors and categorize them"""
    bl_idname = "mektools.ot_refresh_actors"
    bl_label = "Refresh Actors"

    def execute(self, context):
        scene = context.scene
        scene.actors.clear()

        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.data: 
                actor = scene.actors.add()
                actor.armature = obj

        return {'FINISHED'}


class MEKTOOLS_OT_ACTORS_DeleteActor(bpy.types.Operator):
    bl_idname = "mektools.ot_delete_actor"
    bl_label = "Delete Actor"

    def execute(self, context):
        scene = context.scene
        if len(scene.actors) > 0 and 0 <= scene.actors_index < len(scene.actors):
            actor = scene.actors[scene.actors_index]
            if actor.armature:
                bpy.data.objects.remove(actor.armature, do_unlink=True)
            scene.actors.remove(scene.actors_index)
            scene.actors_index = max(0, scene.actors_index - 1)
        return {'FINISHED'}
    
class MEKTOOLS_OT_ACTORS_AddActorProperties(bpy.types.Operator):
    bl_idname = "mektools.ot_add_actor_properties"
    bl_label = "Add Actor Properties"

    def execute(self, context):
        scene = context.scene
        if len(scene.actors) > 0 and 0 <= scene.actors_index < len(scene.actors):
            actor = scene.actors[scene.actors_index]
            if actor.armature:
                actors.add_actor_properties(actor.armature, "Unknown Actor", "custom", True)
                
        bpy.ops.mektools.ot_refresh_actors()
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
    
    actor_name: bpy.props.StringProperty()
    hide_armature: bpy.props.BoolProperty(default=False)
    hide_actor: bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        scene = context.scene
        actor = bpy.data.objects.get(self.actor_name)

        if not actor:
            return {'CANCELLED'}

        actor_item = next((a for a in scene.actors if a.armature == actor), None)

        if actor_item is None:
            return {'CANCELLED'}
         
        actor_item.armature.data["mektools_actor_hide_armature"] = self.hide_armature
        actor_item.armature.data["mektools_actor_hide_actor"] = self.hide_actor
        
        def safe_hide_set(obj, hide):
            if obj and obj.name in context.view_layer.objects:
                obj.hide_set(hide)

        # Ensure actor armature is hidden if actor is hidden
        if self.hide_actor:
            self.hide_armature = True

        # Toggle armature visibility
        safe_hide_set(actor, self.hide_armature)

        # Toggle actor visibility (all parented objects)
        for child in actor.children:
            safe_hide_set(child, self.hide_actor)

        

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
    
    
def register():
    bpy.utils.register_class(MEKTOOLS_OT_ACTORS_AddActorProperties)
    bpy.utils.register_class(MEKTOOLS_OT_ToggleActorVisibility)
    bpy.utils.register_class(MEKTOOLS_OT_Set_Is_Actor)
    bpy.utils.register_class(MEKTOOLS_OT_ToggleHideNonActors)
    bpy.utils.register_class(MEKTOOLS_OT_ACTORS_DeleteActor)
    bpy.utils.register_class(MEKTOOLS_OT_ACTORS_RefreshActors)
    
    bpy.types.Scene.hide_non_actors = bpy.props.BoolProperty(name="Hide Non-Actors", default=False)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_ACTORS_AddActorProperties)
    bpy.utils.unregister_class(MEKTOOLS_OT_ToggleActorVisibility)
    bpy.utils.unregister_class(MEKTOOLS_OT_Set_Is_Actor)
    bpy.utils.unregister_class(MEKTOOLS_OT_ToggleHideNonActors)
    bpy.utils.unregister_class(MEKTOOLS_OT_ACTORS_DeleteActor)
    bpy.utils.unregister_class(MEKTOOLS_OT_ACTORS_RefreshActors)