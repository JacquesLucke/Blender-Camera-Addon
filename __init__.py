import bpy

cameraRigPropertyName = "Camera Rig Type"
settingsPropertyName = "Settings Object"
rotatingCameraType = "ROTATING"   

def insertRotatingCamera():
	
	position = bpy.context.scene.cursor_location
	if bpy.context.scene.objects.active:
		position = bpy.context.scene.objects.active.location
	
	bpy.ops.mesh.primitive_circle_add(location = [0, 0, 0])
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
	
	setParent(rotationControler, positionControler)
	setParent(camera, rotationControler)
	setParent(targetControler, mainControler)
	setParent(positionControler, mainControler)
	
	setCustomProperty(rotationControler, "rotationProgress", 0.0, -1000.0, 1000.0)
	driver = newDriver(rotationControler, "rotation_euler", 2, "SCRIPTED")
	linkFloatPropertyToDriver(driver, "var", rotationControler, "rotationProgress")
	driver.expression = "var * 2 * pi"
	
	lockCurrentLocalRotation(rotationControler, zAxes = False)
	lockCurrentLocalLocation(rotationControler)
	lockCurrentLocalScale(rotationControler)
	lockCurrentLocalRotation(targetControler)
	lockCurrentLocalLocation(camera)
	
	setTrackTo(camera, targetControler)  
	
	mainControler.location = position
	
	
	setCustomProperty(mainControler, cameraRigPropertyName, rotatingCameraType)
	setCustomProperty(targetControler, cameraRigPropertyName, rotatingCameraType)
	setCustomProperty(positionControler, cameraRigPropertyName, rotatingCameraType)
	setCustomProperty(rotationControler, cameraRigPropertyName, rotatingCameraType)
	setCustomProperty(camera, cameraRigPropertyName, rotatingCameraType)
	
	settingsObjectName = rotationControler.name
	setCustomProperty(mainControler, settingsPropertyName, settingsObjectName)
	setCustomProperty(targetControler, settingsPropertyName, settingsObjectName)
	setCustomProperty(positionControler, settingsPropertyName, settingsObjectName)
	setCustomProperty(rotationControler, settingsPropertyName, settingsObjectName)
	setCustomProperty(camera, settingsPropertyName, settingsObjectName)
	
	deselectAll()
	mainControler.select = True

	
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
	
def setCustomProperty(object, propertyName, value, min = -100000000.0, max = 100000000.0):
	object[propertyName] = value
	object["_RNA_UI"] = { propertyName: {"min": min, "max": max} } 
	
def newDriver(object, dataPath, index = -1, type = "SCRIPTED"):
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
		
		
		
def lockCurrentLocalLocation(object, xAxes = True, yAxes = True, zAxes = True):
	setActive(object)
	constraint = object.constraints.new(type = "LIMIT_LOCATION")
	constraint.owner_space = "LOCAL"
	
	setConstraintLimitData(constraint, object.location)
	
	constraint.use_min_x = xAxes
	constraint.use_max_x = xAxes
	constraint.use_min_y = yAxes
	constraint.use_max_y = yAxes
	constraint.use_min_z = zAxes
	constraint.use_max_z = zAxes
	
def lockCurrentLocalRotation(object, xAxes = True, yAxes = True, zAxes = True):
	setActive(object)
	constraint = object.constraints.new(type = "LIMIT_ROTATION")
	constraint.owner_space = "LOCAL"
	
	setConstraintLimitData(constraint, object.rotation_euler)
	
	constraint.use_limit_x = xAxes
	constraint.use_limit_y = yAxes
	constraint.use_limit_z = zAxes
	
def lockCurrentLocalScale(object, xAxes = True, yAxes = True, zAxes = True):
	setActive(object)
	constraint = object.constraints.new(type = "LIMIT_SCALE")
	constraint.owner_space = "LOCAL"
	
	setConstraintLimitData(constraint, object.scale)
	
	constraint.use_min_x = xAxes
	constraint.use_max_x = xAxes
	constraint.use_min_y = yAxes
	constraint.use_max_y = yAxes
	constraint.use_min_z = zAxes
	constraint.use_max_z = zAxes
	
def setConstraintLimitData(constraint, vector):
	(x, y, z) = vector
	constraint.min_x = x
	constraint.max_x = x
	constraint.min_y = y
	constraint.max_y = y
	constraint.min_z = z
	constraint.max_z = z
	
	
def getCurrentSettingsObjectOrNothing():
	activeObject = bpy.context.active_object
	if isPartOfRotatingCamera(activeObject):
		return bpy.data.objects[activeObject[settingsPropertyName]]
	
def isPartOfRotatingCamera(object):
	if object:
		if settingsPropertyName in object:
			return True
	return False
	
	
def insertTimeBasedRotationAnimation():
	settingsObject = getCurrentSettingsObjectOrNothing()
	if settingsObject:
		driver = newDriver(settingsObject, '["rotationProgress"]')
		driver.expression = "frame / 100"
	
	
	
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
		
		settingsObject = getCurrentSettingsObjectOrNothing()
		if settingsObject:  
			col.operator("animation.insert_time_rotation_animation")
			self.layout.prop(settingsObject, '["rotationProgress"]', text = "Rotations", slider = False)
		
		
		
class AddRotatingCameraOperator(bpy.types.Operator):
	bl_idname = "animation.add_rotating_camera"
	bl_label = "Add Rotating Camera"
	
	def execute(self, context):
		insertRotatingCamera()
		return{"FINISHED"}

class InsertTimeBasedRotationAnimation(bpy.types.Operator):
	bl_idname = "animation.insert_time_rotation_animation"
	bl_label = "Auto Animation"
	
	def execute(self, context):
		insertTimeBasedRotationAnimation()
		return{"FINISHED"}




#registration

def register():
	bpy.utils.register_class(CameraToolsPanel)
	bpy.utils.register_class(AddRotatingCameraOperator)
	bpy.utils.register_class(InsertTimeBasedRotationAnimation)

def unregister():
	bpy.utils.unregister_class(CameraToolsPanel)
	bpy.utils.unregister_class(InsertTimeBasedRotationAnimation)

if __name__ == "__main__":
	register()



