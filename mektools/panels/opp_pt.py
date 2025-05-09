import bpy

def draw_curve_menu(self, context):
    self.layout.operator("mektools.append_projection_plane", text="Projection Plane", icon="MESH_GRID")

def register():
    bpy.types.VIEW3D_MT_curve_add.append(draw_curve_menu)

def unregister():
    bpy.types.VIEW3D_MT_curve_add.remove(draw_curve_menu)
