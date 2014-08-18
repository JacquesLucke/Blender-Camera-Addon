import bpy, math

def insertRotatingCamera():
    
    bpy.ops.mesh.primitive_circle_add(location = [0, 0, -2])
    control = bpy.ops.object
    
    bpy.ops.object.empty_add(location = [0, 0, 0], type = "SPHERE")
    targetControler = bpy.context.object
    targetControler.empty_draw_size = 0.2
    
    bpy.ops.object.empty_add(location = [0, 0, 1.5], type = "CIRCLE")
    positionControler = bpy.context.object
    positionControler.scale = [5, 5, 5]
    positionControler.rotation_euler.x = 90 / 180 * math.pi
    
    bpy.ops.object.camera_add(location = [0, -5, 1.5])
    camera = bpy.context.object
    
    camera.select = True
    bpy.context.scene.objects.active = targetControler
    bpy.ops.object.track_set(type = "TRACKTO")
    
    
insertRotatingCamera()

