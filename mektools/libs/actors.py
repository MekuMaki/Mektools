import bpy

def update_selected_actor(self, context):
    scene = context.scene
    if len(scene.actors) > 0 and 0 <= scene.actors_index < len(scene.actors):
        actor = scene.actors[scene.actors_index]
        if actor.armature:
            previous_mode = context.object.mode if context.object else 'OBJECT'
            bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.select_all(action='DESELECT')
            actor.armature.select_set(True)
            context.view_layer.objects.active = actor.armature

            try:
                bpy.ops.object.mode_set(mode=previous_mode)
            except RuntimeError:
                bpy.ops.object.mode_set(mode='OBJECT') 
                
def add_actor_properties(armature, name = "Unkown Actor", armature_type = "unkown", is_actor = True, collection = None):
    """Adds custom properties to an armature data block."""
    if armature and armature.type == 'ARMATURE':
        if collection != None:
            armature.data["mektools_actor_collection"] = collection
        armature.data["mektools_actor_name"] = name
        armature.data["mektools_is_actor"] = is_actor
        armature.data["mektools_armature_type"] = armature_type
        
            # Force Blender to update the UI
        bpy.context.view_layer.update()
        for area in bpy.context.screen.areas:
            if area.type == "PROPERTIES":  # Update Properties Panel
                area.tag_redraw()