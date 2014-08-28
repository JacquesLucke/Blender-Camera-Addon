import bpy

def newEmpty(name = "Empty", location = [0, 0, 0], hide = False):
	bpy.ops.object.empty_add(location = location, type = "PLAIN_AXES")
	empty = bpy.context.object
	empty.name = name
	if hide:
		bpy.ops.object.hide_view_set(unselected = False)
	return empty
	
def newText(name = "Text", location = [0, 0, 0], text = "text"):
	bpy.ops.object.text_add(location = location)
	textObject = bpy.context.object
	textObject.name = name
	textObject.data.body = text
	return textObject

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
	
def setParentWithoutInverse(child, parent):
	deselectAll()
	child.select = True
	setActive(parent)
	bpy.ops.object.parent_no_inverse_set()
	
def setCustomProperty(object, propertyName, value, min = -1000000.0, max = 1000000.0):
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
	driverVariable.targets[0].data_path = dataPath
	
def deselectAll():
	bpy.ops.object.select_all(action = "DESELECT")
	
def getActive():
	return bpy.context.scene.objects.active
	
def setActive(object):
	object.select = True
	bpy.context.scene.objects.active = object
	
def deleteSelectedObjects():
	bpy.ops.object.delete(use_global=False)
	
def isObjectReferenceSet(object, name):
	if name in object.constraints:
		constraint = object.constraints[name]
		if constraint.name == name:
			if constraint.target:
				return True
	return False

def getChildOfConstraintWithName(object, name):
	if name not in object.constraints:
		constraint = object.constraints.new(type = "CHILD_OF")
		constraint.name = name
	return object.constraints[name]

def setObjectReference(object, name, target):
	if isObjectReferenceSet(object, name):
		object.constraints[name].target = target
	else:
		constraint = getChildOfConstraintWithName(object, name)
		constraint.influence = 0
		constraint.target = target
		constraint.show_expanded = False
		
def getObjectReference(object, name):
	if isObjectReferenceSet(object, name):
		return object.constraints[name].target
	return None

def removeObjectReference(object, name):
	if name in object.constraints:
		object.constraints.remove(object.constraints[name])
		
def lockCurrentTransforms(object):
	lockCurrentLocalLocation(object)
	lockCurrentLocalRotation(object)
	lockCurrentLocalScale(object)
		
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
	
def deleteAllConstraints(object):
	for constraint in object.constraints:
		object.constraints.remove(constraint)
		
def textToName():
	for object in bpy.data.objects:
		if hasattr(object.data, "body"):
			object.name = object.data.body
			
def seperateTextObject(textObject, seperator = "\n"):
	textList = textObject.data.body.split(seperator)
	for i in range(len(textList)):
		newText(name = textList[i], location = [0, -i, 0], text = textList[i])
	
def clearAnimation(object, dataPath):
	try:
		for fcurve in object.animation_data.action.fcurves:
			if fcurve.data_path == dataPath:
				for keyframe in fcurve.keyframe_points:
					object.keyframe_delete(dataPath, frame = keyframe.co.x)
				for keyframe in fcurve.keyframe_points:
					object.keyframe_delete(dataPath, frame = keyframe.co.x)
	except:
		print("can't delete animation")
		
def slowAnimationOnEachKeyframe(object, dataPath):
	try:
		for fcurve in object.animation_data.action.fcurves:
			if fcurve.data_path == dataPath:
				for keyframe in fcurve.keyframe_points:
					keyframe.handle_left.y = keyframe.co.y
					keyframe.handle_right.y = keyframe.co.y
	except:
		print("can't change keyframes")
		
def getSelectedObjects():
	return bpy.context.selected_objects
def setSelectedObjects(selection):
	deselectAll()
	for object in selection:
		object.select = True
		setActive(object)
		
def isTextObject(object):
	if hasattr(object, "data"):
		if hasattr(object.data, "body"):
			return True
	return False
	
def delete(object):
	deselectAll()
	object.hide = False
	setActive(object)
	bpy.ops.object.delete()
					