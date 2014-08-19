import bpy

def insertRotatingCamera():
    
    position = bpy.context.scene.cursor_location
    if bpy.context.scene.objects.active:
        position = bpy.context.scene.objects.active.location
    
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
    
    driver = newDriver(rotationControler, "rotation_euler", 2, "SCRIPTED")
    linkFloatPropertyToDriver(driver, "var", rotationControler, "rotationProgress")
    driver.expression = "var * 2 * pi"
    
    mainControler.location = position
    mainControler.location.z -= 2

    #bpy.context.scene.objects.active = camera
    #bpy.ops.view3d.object_as_camera()

    
def setTrackTo(child, trackTo):
    deselectAll()
    child.select = True
    bpy.context.scene.objects.active = trackTo
    bpy.ops.object.track_set(type = "TRACKTO")   

def setParent(child, parent):
    deselectAll()
    child.select = True
    bpy.context.scene.objects.active = parent
    bpy.ops.object.parent_set(type = "OBJECT", keep_transform = True)
    
def setCustomProperty(object, propertyName, value, min, max):
    object[propertyName] = value
    object["_RNA_UI"] = { propertyName: {"min": min, "max": max} } 
    
def newDriver(object, dataPath, index, type):
    fcurve = object.driver_add(dataPath, index)
    driver = fcurve.driver
    driver.type = type
    return driver

def linkFloatPropertyToDriver(driver, name, id, dataPath):
    driverVariable = driver.variables.new()
    driverVariable.name = name
    driverVariable.type = "SINGLE_PROP"
    driverVariable.targets[0].id = id
    driverVariable.targets[0].data_path = '["' + dataPath + '"]'
    
def deselectAll():
    bpy.ops.object.select_all(action = "DESELECT")


insertRotatingCamera()


