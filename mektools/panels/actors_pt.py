import bpy
from bpy.types import Panel
from ..addon_preferences import get_addon_preferences 
from ..libs import actors

class ActorItem(bpy.types.PropertyGroup):
    """Stores an armature reference for the UI list with differentiation"""
    name: bpy.props.StringProperty(name="Armature Name")
    armature: bpy.props.PointerProperty(type=bpy.types.Object)
    armature_type: bpy.props.StringProperty(name="Armature Type", default="Unknown")

class UI_UL_Actors(bpy.types.UIList):
    """List UI for displaying categorized armatures"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            icon_type = 'GHOST_DISABLED'
            
            if item.armature_type == "mekrig":
                icon_type = 'OUTLINER_OB_ARMATURE'
            elif item.armature_type != "Unknown":
                icon_type = 'MOD_ARMATURE'
            
            layout.label(text=item.name, icon=icon_type)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='OUTLINER_OB_ARMATURE')
            
       
class MEKTOOLS_PT_Actors(Panel):
    bl_idname = "mektools.pt_actors"
    bl_label = "Actors"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mektools"
    
    @classmethod
    def poll(cls, context):
        return get_addon_preferences().ex_actors == 'ON'
    
    def draw(self, context):
        scene = context.scene
        self.prefs = get_addon_preferences()
      
        layout = self.layout
        box = layout.box()
        row = box.split(factor=0.63)
        row.label(text="Available Actors")
        row.operator("mektools.ot_refresh_actors", icon="FILE_REFRESH", text="Refresh")
            
        row = box.row()
        row.template_list("UI_UL_Actors", "", scene, "actors", scene, "actors_index")

        col = row.column(align=True)
        col.operator("mektools.ot_refresh_actors", icon="ADD", text="")  # Add aka import 
        col.operator("mektools.ot_refresh_actors", icon="REMOVE", text="")  # delete / remove 
        
        col.separator(factor=1.0)
        
        col.operator("mektools.ot_refresh_actors", icon="GREASEPENCIL", text="") # rename actor 
        col.operator("mektools.ot_refresh_actors", icon="DUPLICATE", text="")  # duplicate 
        
        col.separator(factor=1.0)
        col.operator("mektools.ot_refresh_actors", icon="TRIA_UP", text="")  # hierachy up 
        col.operator("mektools.ot_refresh_actors", icon="TRIA_DOWN", text="")  # hierachy down
        
        row = layout.row(align=True)
        if len(scene.actors) > 0 and 0 <= scene.actors_index < len(scene.actors):
            actor = scene.actors[scene.actors_index]
            if "mektools_is_actor" in actor.armature.data.keys() and actor.armature.data["mektools_is_actor"]:    
                row.operator("mektools.ot_refresh_actors", text="Migrate Rig") # migrate to mekrig 
                row.operator("mektools.ot_refresh_actors", text="Reimport Mesh") # reimport mesh
            else:
                row.operator("mektools.ot_add_actor_properties", icon="ADD", text="Make Actor") # adds actor properties this should later on only be displayed if its an unknown armature
        
           

def register():
    bpy.utils.register_class(ActorItem)
    bpy.utils.register_class(UI_UL_Actors)

    bpy.types.Scene.actors = bpy.props.CollectionProperty(type=ActorItem)
    bpy.types.Scene.actors_index = bpy.props.IntProperty()
    bpy.types.Scene.actors_index = bpy.props.IntProperty(update=actors.update_selected_actor)
    
    bpy.utils.register_class(MEKTOOLS_PT_Actors)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_PT_Actors)
    del bpy.types.Scene.actors
    del bpy.types.Scene.actors_index

    bpy.utils.unregister_class(ActorItem)
    bpy.utils.unregister_class(UI_UL_Actors)
    del bpy.types.Scene.orientation_mode
    
    
    
    
    