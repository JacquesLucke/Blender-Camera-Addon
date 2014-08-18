import bpy

def insertRotatingCamera():
    bpy.ops.mesh.primitive_circle_add(location = [0, 0, -2])
    control = bpy.ops.object
    
    bpy.ops.object.empty_add(location = [0, 0, 0], type = "SPHERE")
    positionControler = bpy.context.object
    positionControler.empty_draw_size = 0.2
    
    
    
insertRotatingCamera()

