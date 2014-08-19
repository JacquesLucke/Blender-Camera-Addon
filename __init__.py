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
    
    lockObjectToCurrentLocalLocation(rotationControler)

    #bpy.context.scene.objects.active = camera
    #bpy.ops.view3d.object_as_camera()

    
def setTrackTo(child, trackTo):
    deselectAll()
    child.select = True
    setActive(trackTo)
    bpy.ops.object.track_set(type = "TRACKTO")   

def setParent(child, parent):
    deselectAll()
    child.select = True
    setActive(parent)
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
    
def setActive(object):
    bpy.context.scene.objects.active = object
    
def lockObjectToCurrentLocalLocation(object):
    setActive(object)
    constraint = object.constraints.new(type='LIMIT_LOCATION')
    constraint.owner_space = "LOCAL"
    
    (x, y, z) = object.location
    
    constraint.min_x = x
    constraint.max_x = x
    constraint.min_y = y
    constraint.max_y = y
    constraint.min_z = z
    constraint.max_z = z
    
    constraint.use_min_x = True
    constraint.use_max_x = True
    constraint.use_min_y = True
    constraint.use_max_y = True
    constraint.use_min_z = True
    constraint.use_max_z = True
    
# interface

class CameraToolsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Animation"
    bl_label = "Camera Tools"
    
    def draw(self, context):
        layout = self.layout
        
        split = layout.split()
        col = split.column(align = True)
        
        col.operator("animation.add_rotating_camera")
        
class AddRotatingCameraOperator(bpy.types.Operator):
    bl_idname = "animation.add_rotating_camera"
    bl_label = "Add Rotating Camera"
    
    def execute(self, context):
        insertRotatingCamera()
        return{"FINISHED"}





#registration

def register():
    bpy.utils.register_class(CameraToolsPanel)
    bpy.utils.register_class(AddRotatingCameraOperator)

def unregister():
    bpy.utils.unregister_class(CameraToolsPanel)
    bpy.utils.unregister_class(AddRotatingCameraOperator)

if __name__ == "__main__":
    register()


