import bpy, math

def insertRotatingCamera():
    
    bpy.ops.mesh.primitive_circle_add(location = [0, 0, -2])
    mainControler = bpy.context.object
    
    bpy.ops.object.empty_add(location = [0, 0, 0], type = "SPHERE")
    targetControler = bpy.context.object
    targetControler.empty_draw_size = 0.2
    
    bpy.ops.mesh.primitive_circle_add(location = [0, 0, 1.5])
    positionControler = bpy.context.object
    positionControler.scale = [5, 5, 5]
    
    bpy.ops.object.empty_add(location = [0, 0, 1.5], type = "PLAIN_AXES")
    rotationControler = bpy.context.object
    rotationControler.empty_draw_size = 0.2
    
    bpy.ops.object.camera_add(location = [0, -5, 1.5])
    camera = bpy.context.object
    
    setTrackTo(camera, targetControler)    
    setParent(rotationControler, positionControler)
    setParent(camera, rotationControler)
    setParent(targetControler, mainControler)
    setParent(positionControler, mainControler)
    
    setCustomProperty(rotationControler, "rotationProgress", 0.0, -1000.0, 1000.0)
    
def setTrackTo(child, trackTo):
    bpy.ops.object.select_all(action = "DESELECT")
    child.select = True
    bpy.context.scene.objects.active = trackTo
    bpy.ops.object.track_set(type = "TRACKTO")   

def setParent(child, parent):
    bpy.ops.object.select_all(action = "DESELECT")
    child.select = True
    bpy.context.scene.objects.active = parent
    bpy.ops.object.parent_set(type = "OBJECT", keep_transform = True)
    
def setCustomProperty(object, propertyName, value, min, max):
    object[propertyName] = value
    object["_RNA_UI"] = { propertyName: {"min": min, "max": max} } 
    
insertRotatingCamera()

