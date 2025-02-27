import bpy

def update_selected_actor(self, context):
    """Updates selection based on active actor index while respecting Shift selection."""
    scene = context.scene
    if len(scene.actors) > 0 and 0 <= scene.actors_index < len(scene.actors):
        if scene.actors_index >= 0:
            actor = scene.actors[scene.actors_index]
            if actor.armature:
                previous_mode = context.object.mode if context.object else 'OBJECT'
                if context.view_layer.objects.active:
                    bpy.ops.object.mode_set(mode='OBJECT')
                
                bpy.ops.object.select_all(action='DESELECT')
                actor.armature.select_set(True)
                context.view_layer.objects.active = actor.armature
                
                try:
                    bpy.ops.object.mode_set(mode=previous_mode)
                except RuntimeError:
                    bpy.ops.object.mode_set(mode='OBJECT')

def update_active_actor(scene):
    """Updates the active actor index based on selection."""
    selected_armatures = {obj for obj in bpy.context.selected_objects if obj.type == 'ARMATURE'}
    # Find the first actor whose armature is in the selected armatures
    new_index = -1
    for i, actor in enumerate(scene.actors):
        if actor.armature in selected_armatures:
            new_index = i
            break
    
    # Only update if the index has changed to prevent recursion
    if scene.actors_index != new_index:     
        scene.actors_index = new_index                  
                
def cleanup_actor_list(scene):
    """Calls the delete operator for actors referencing armatures that are no longer in the viewport.""" 
    to_remove = []
    
    for i, actor in enumerate(scene.actors):
        if actor.armature and actor.armature not in bpy.context.view_layer.objects.values():
            to_remove.append(i)  
    
    for i in reversed(to_remove):
        scene.actors.remove(i)
        

def on_update_callback(scene):
    """Callback function triggered when Blender's update operation is called."""
    remove_callback()  # Temporarily disable callback
    update_active_actor(scene) 
    cleanup_actor_list(scene)
    add_callback()  # Re-enable callback
    
def add_callback():
    """Ensures the callback is only added once."""
    if on_update_callback not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_update_callback)

def remove_callback():
    """Removes the callback to prevent infinite recursion."""
    if on_update_callback in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_update_callback)


        