import bpy, math

def insertRotatingCamera():
    
    bpy.ops.mesh.primitive_circle_add(location = [0, 0, -2])
    control = bpy.ops.object
    
    bpy.ops.object.empty_add(location = [0, 0, 0], type = "SPHERE")
    targetControler = bpy.context.object
    targetControler.empty_draw_size = 0.2
    
    bpy.ops.mesh.primitive_circle_add(location = [0, 0, 1.5])
    positionControler = bpy.context.object
    positionControler.scale = [5, 5, 5]
    
    bpy.ops.object.camera_add(location = [0, -5, 1.5])
    camera = bpy.context.object
    
    bpy.ops.object.select_all(action = "DESELECT")
    camera.select = True
    bpy.context.scene.objects.active = targetControler
    bpy.ops.object.track_set(type = "TRACKTO")
    
    bpy.ops.object.select_all(action = "DESELECT")
    camera.select = True
    bpy.context.scene.objects.active = positionControler
    bpy.ops.object.parent_set(type = "OBJECT", keep_transform = True)
    
    
insertRotatingCamera()

