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
        