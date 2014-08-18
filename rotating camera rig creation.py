import bpy, math

def insertRotatingCamera():
    
    bpy.ops.mesh.primitive_circle_add(location = [0, 0, -2])
    control = bpy.ops.object
    
    bpy.ops.object.empty_add(location = [0, 0, 0], type = "SPHERE")
    positionControler = bpy.context.object
    positionControler.empty_draw_size = 0.2
    
    bpy.ops.object.empty_add(location = [0, 0, 1.5], type = "CIRCLE")
    targetControler = bpy.context.object
    targetControler.scale = [5, 5, 5]
    targetControler.rotation_euler.x = 90 / 180 * math.pi
    
    bpy.ops.object.camera_add(location = [0, -5, 1.5])
    camera = bpy.context.object
    
    
insertRotatingCamera()

