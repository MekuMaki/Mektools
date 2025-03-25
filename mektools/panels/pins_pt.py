import bpy
from bpy.types import Panel
from ..addon_preferences import get_addon_preferences 
from ..libs import pins, helper
from ..custom_icons import preview_collections

class ItemPin(bpy.types.PropertyGroup):
    """Stores an obj reference for the UI list with differentiation"""
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    
    @property
    def hide_armature(self):
        return self.object and self.object.get("mt_pin_hide_armature", False)
    
    @property
    def hide_object(self):
        return self.object and self.object.get("mt_pin_hide_object", False)  

class UI_UL_Pins(bpy.types.UIList):
    """List UI for displaying categorized Pins"""
    
    def draw_filter(self, context, layout):
        """Draws the filter UI inside the list panel."""
        layout.prop(context.scene, "hide_ghosts", text="Filter Ghosts", toggle=True)
        
    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        filtered = []
        order = []
        hide_ghosts = context.scene.hide_ghosts
    
        for i, item in enumerate(items):
            flag = self.bitflag_filter_item 

            if hide_ghosts and item.object not in bpy.context.view_layer.objects.values():  # Hides objects that are not in the Scene but in the blend file. This happens if the item was deleted but still has a user.
                flag &= ~self.bitflag_filter_item  
        
            filtered.append(flag)
            order.append(i)
    
        return filtered, order
        
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname): 
        obj = item.object      
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if obj:
                if obj in bpy.context.view_layer.objects.values():
                    icon_id = helper.get_object_icon(obj)
                else: 
                    icon_id = "GHOST_DISABLED"

            
                row = layout.row(align=True)
                row.active = not item.hide_object
                row.label(text=obj.name, icon=icon_id)
           
                hide_armature_icon = preview_collections["main"]["BONE_DATA_OFF"].icon_id
                # Hide Armature Button
                if item.hide_armature:
                    op = row.operator("mektools.ot_toggle_pin_visibility", text="", icon_value=hide_armature_icon, emboss=False)
                else:
                    op = row.operator("mektools.ot_toggle_pin_visibility", text="", icon="BONE_DATA", emboss=False)
                op.object_name = obj.name
                op.hide_armature = not item.hide_armature
                op.hide_object = item.hide_object

                # Hide Object Button
                op = row.operator("mektools.ot_toggle_pin_visibility", text="", icon='HIDE_ON' if item.hide_object else 'HIDE_OFF', emboss=False)
                op.object_name = obj.name
                op.hide_armature = item.hide_armature
                op.hide_object =  not item.hide_object
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='OUTLINER_OB_ARMATURE')
            
       
class MEKTOOLS_PT_Pins(Panel):
    bl_idname = "mektools.pt_pins"
    bl_label = "Pins"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mektools"
    
    @classmethod
    def poll(cls, context):
        return get_addon_preferences().ex_pins == 'ON'
    
    def draw(self, context):
        scene = context.scene
        self.prefs = get_addon_preferences()
      
        layout = self.layout
        box = layout.box()
        row = box.split(factor=0.63)
        row.label(text="Pins")
            
        row = box.row()
        row.template_list("UI_UL_Pins", "", scene, "pins", scene, "pins_index")

        col = row.column(align=True)
        op = col.operator("mektools.ot_set_is_pinned", icon="ADD", text="") 
        op.is_pin = True
        op = col.operator("mektools.ot_set_is_pinned", icon="REMOVE", text="")
        op.is_pin = False
        
        col.separator(factor=1.0)
        
        if len(scene.pins) > 0 and 0 <= scene.pins_index < len(scene.pins):
            col.operator("mektools.ot_duplicate_pin", icon="DUPLICATE", text="")  
            col.operator("mektools.ot_delete_pin", icon="TRASH", text="")  
        
        
           

def register():
    bpy.utils.register_class(ItemPin)
    bpy.utils.register_class(UI_UL_Pins)

    bpy.types.Scene.pins = bpy.props.CollectionProperty(type=ItemPin)
    #bpy.types.Scene.pins_index = bpy.props.IntProperty()
    bpy.types.Scene.pins_index = bpy.props.IntProperty(update=pins.select_pin)
    
    bpy.types.Scene.hide_ghosts = bpy.props.BoolProperty(name="Hide Ghosts", default=True)
    bpy.types.Scene.suppress_pins = bpy.props.BoolProperty(name="supressPinList", default=False)
    
    bpy.utils.register_class(MEKTOOLS_PT_Pins)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_PT_Pins)
    del bpy.types.Scene.pins
    del bpy.types.Scene.pins_index
    del bpy.types.Scene.hide_ghosts
    del bpy.types.Scene.suppress_pins

    bpy.utils.unregister_class(ItemPin)
    bpy.utils.unregister_class(UI_UL_Pins)
    del bpy.types.Scene.orientation_mode
    
    
    
    
    