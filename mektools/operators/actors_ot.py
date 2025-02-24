import bpy
            
class MEKTOOLS_OT_ACTORS_RefreshActors(bpy.types.Operator):
    """Refresh the list of actors and categorize them"""
    bl_idname = "mektools.ot_refresh_actors"
    bl_label = "Refresh Actors"

    def execute(self, context):
        scene = context.scene
        scene.actors.clear()

        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.data:
                armature_type = "Unknown"
                actor_name = obj.data.get("mektools_actor_name", "Unknown actor")
                
                # Check for mektools properties stored in Armature data block
                if "mektools_is_actor" in obj.data.keys() and obj.data["mektools_is_actor"]:
                    armature_type = obj.data.get("mektools_armature_type", "Unknown")
                else:
                    actor_name = "Unknown Armature"
                
                actor = scene.actors.add()
                actor.name = actor_name
                actor.armature = obj
                actor.armature_type = armature_type

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
    
    
def register():
    bpy.utils.register_class(MEKTOOLS_OT_ACTORS_DeleteActor)
    bpy.utils.register_class(MEKTOOLS_OT_ACTORS_RefreshActors)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_ACTORS_DeleteActor)
    bpy.utils.unregister_class(MEKTOOLS_OT_ACTORS_RefreshActors)