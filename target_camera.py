import bpy, math
from utils import *

cameraRigPropertyName = "Camera Rig Type"
targetCameraType = "TARGET" 
keyframeDistancePropertyName = "Keyframe Distance"

targetCameraName = "TARGET CAMERA"
dataEmptyName = "TARGET CAMERA CONTAINER"

useListSeparator = False

calculatedTargetAmount = 0


# insert basic camera setup
#################################

def insertTargetCamera():
	oldSelection = getSelectedObjects()

	camera = newCamera()
	movement = newMovementEmpty()
	dataEmpty = newDataEmpty()
	
	movement.parent = dataEmpty
	setParentWithoutInverse(camera, movement)
	camera.location.z = 4
	setActive(camera)
	bpy.context.object.data.dof_object = movement
	
	setSelectedObjects(oldSelection)
	newTargets()
	
def newCamera():
	bpy.ops.object.camera_add(location = [0, 0, 0])
	camera = bpy.context.object
	camera.name = targetCameraName
	camera.rotation_euler = [0, 0, 0]
	setCustomProperty(camera, cameraRigPropertyName, targetCameraType)
	setCustomProperty(camera, keyframeDistancePropertyName, 40, min = 1)
	return camera
	
def newMovementEmpty():
	movement = newEmpty(name = "Movement Empty", location = [0, 0, 0])
	movement.empty_draw_size = 0.2
	return movement
	
def newDataEmpty():
	dataEmpty = newEmpty(name = dataEmptyName, location = [0, 0, 0])
	setCustomProperty(dataEmpty, "travel", 1.0, min = 1.0)
	setCustomProperty(dataEmpty, "stops", [])
	dataEmpty.hide = True
	lockCurrentTransforms(dataEmpty)
	return dataEmpty
	
	
# create animation
###########################

def recalculateAnimation():
	createFullAnimation(getTargetList())
	
def createFullAnimation(targetList):
	global calculatedTargetAmount
	cleanupScene(targetList)
	removeAnimation()

	movement = getMovementEmpty()
	dataEmpty = getDataEmpty()
	deleteAllConstraints(movement)
	
	for target in targetList:
		createConstraintSet(target)
		
	createTravelToConstraintDrivers()
	createTravelAnimation()
	calculatedTargetAmount = getTargetAmount()
	
def cleanupScene(targetList):
	deselectAll()
	for object in bpy.context.scene.objects:
		if isTargetName(object.name) and object not in targetList:
			object.select = True
			object.hide = False
	bpy.ops.object.delete()	
	
def removeAnimation():
	clearAnimation(getDataEmpty(), '["travel"]')
	
def createConstraintSet(target):
	movement = getMovementEmpty()
	constraint = movement.constraints.new(type = "COPY_TRANSFORMS")
	constraint.target = target
	constraint.influence = 0
	constraint.show_expanded = False
	
def createTravelToConstraintDrivers():
	movement = getMovementEmpty()
	dataEmpty = getDataEmpty()
	constraints = movement.constraints
	
	for i in range(getTargetAmount()):
		constraint = constraints[i]
		driver = newDriver(movement, 'constraints["' + constraint.name + '"].influence')
		linkFloatPropertyToDriver(driver, "var", dataEmpty, '["travel"]')
		driver.expression = "var - " + str(i)
		
def createTravelAnimation():
	dataEmpty = getDataEmpty()
	stops = []
	
	for i in range(getTargetAmount()):
		frame = i * getKeyframeDistance() + 1
		dataEmpty["travel"] = float(i + 1)
		dataEmpty.keyframe_insert(data_path='["travel"]', frame = frame)
		stops.append(frame)
		
	slowAnimationOnEachKeyframe(dataEmpty, '["travel"]')
	setStops(dataEmpty, stops)

	
# target operations
#############################

def newTargets():
	targets = getTargetList()
	selectedObjects = []
	for object in getSelectedObjects():
		if not (object == getTargetCamera() or object == getMovementEmpty()):
			selectedObjects.append(object)
		
	selectedObjects.reverse()
	for object in selectedObjects:
		targets.append(newRealTarget(object))
	createFullAnimation(targets)
	
def newRealTarget(target):
	if isValidTarget(target): return target
	
	deselectAll()
	setActive(target)
	bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY')

	empty = newEmpty(name = "REAL TARGET", location = [0, 0, 0])
	empty.empty_draw_size = 0.4
	setParentWithoutInverse(empty, target)
	
	setCustomProperty(empty, "loading time", 30, min = 1)
	
	return empty
	
def deleteTarget(index):
	targets = getTargetList()
	del targets[index]
	createFullAnimation(targets)
	
def moveTargetUp(index):
	if index > 0:
		targets = getTargetList()
		targets.insert(index-1, targets.pop(index))
		createFullAnimation(targets)
def moveTargetDown(index):
	targets = getTargetList()
	targets.insert(index+1, targets.pop(index))
	createFullAnimation(targets)
	
def goToNextTarget():
	travel = getTravelValue()
	newTravel = math.floor(travel) + 1
	bpy.context.screen.scene.frame_current = getFrameOfTravelValue(newTravel)
	
def goToPreviousTarget():
	travel = getTravelValue()
	newTravel = math.ceil(travel) - 1
	bpy.context.screen.scene.frame_current = getFrameOfTravelValue(newTravel)
	
def getFrameOfTravelValue(travel):
	travel = max(1, travel)
	stops = getDataEmpty()['stops']
	if len(stops) > 0:
		if travel >= len(stops):
			return stops[-1]
		else:
			return stops[int(travel - 1)]
	else: return 1
	
	
# utilities
#############################

def targetCameraExists():
	if getTargetCamera() is None: return False
	else: return True
def getTargetCamera():
	return bpy.data.objects.get(targetCameraName)
def getMovementEmpty():
	return getTargetCamera().parent
def getDataEmpty():
	return bpy.data.objects.get(dataEmptyName)
			
def isTargetCamera(object):
	return object.name == targetCameraName
	
def selectTargetCamera():
	camera = getTargetCamera()
	if camera:
		deselectAll()
		camera.select = True
		setActive(camera)
		
def selectMovementEmpty():
	deselectAll()
	setActive(getMovementEmpty())
		
def selectTarget(index):
	deselectAll()
	target = getTargetList()[index]
	setActive(target)
		
def getTargetAmount():
	return len(getTargetList())
	
def getTargetList():
	targets = []
	uncleanedTargets = getUncleanedTargetList()
	for target in uncleanedTargets:
		if isValidTarget(target) and target not in targets:
			targets.append(target)
	return targets
	
def isValidTarget(target):
	if hasattr(target, "name"):
		if isTargetName(target.name):
			if hasattr(target, "parent"):
				if hasattr(target.parent, "name"):
					return True
	return False
	
def isTargetName(name):
	return name[:11] == "REAL TARGET"
	
def getKeyframeDistance():
	return getTargetCamera().get(keyframeDistancePropertyName)
	
def getSelectedTargets(targetList):
	objects = getSelectedObjects()
	targets = []
	for object in objects:
		targetsOfObject = getTargetsFromObject(object, targetList)
		for target in targetsOfObject:
			if object not in targets and hasattr(object.parent, "name"):
				targets.append(target)
	return targets
	
def getTargetsFromObject(object, targetList):
	targets = []
	if isValidTarget(object): targets.append(object)
	for target in targetList:
		if target.parent.name == object.name: targets.append(target)
	return targets

def getUncleanedTargetList():
	movement = getMovementEmpty()
	uncleanedTargets = []
	for constraint in movement.constraints:
		if hasattr(constraint, "target"):
			uncleanedTargets.append(constraint.target)
	return uncleanedTargets
	
def getTravelValue():
	return round(getDataEmpty().get("travel"), 3)
	
def setStops(dataEmpty, stops):
	dataEmpty['stops'] = stops
	

		
# interface
#############################

class TargetCameraPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Animation"
	bl_label = "Target Camera"
	bl_context = "objectmode"
	
	@classmethod
	def poll(self, context):
		return targetCameraExists()
	
	def draw(self, context):
		layout = self.layout
		
		camera = getTargetCamera()
		movement = getMovementEmpty()
		dataEmpty = getDataEmpty()
		
		col = layout.column(align = True)
		col.operator("camera_tools.recalculate_animation", text = "Recalculate")
		col.prop(camera, '["' + keyframeDistancePropertyName + '"]', slider = False, text = "Frames per Text")
			
		row = layout.row(align = True)
		row.operator("camera_tools.go_to_previous_target", icon = 'TRIA_LEFT', text = "")
		row.label("Travel: " + str(getTravelValue()))
		row.operator("camera_tools.go_to_next_target", icon = 'TRIA_RIGHT', text = "")
		
		box = layout.box()
		col = box.column(align = True)
		targetList = getTargetList()
		for i in range(len(targetList)):
			row = col.split(percentage=0.6, align = True)
			row.scale_y = 1.35
			name = row.operator("camera_tools.select_target", targetList[i].parent.name)
			name.currentIndex = i
			up = row.operator("camera_tools.move_target_up", icon = 'TRIA_UP', text = "")
			up.currentIndex = i
			down = row.operator("camera_tools.move_target_down", icon = 'TRIA_DOWN', text = "")
			down.currentIndex = i
			delete = row.operator("camera_tools.delete_target", icon = 'X', text = "")
			delete.currentIndex = i
			if useListSeparator: col.separator()
		box.operator("camera_tools.new_target_object", icon = 'PLUS')
			
		row = layout.row(align = True)
		row.label("Select")
		row.operator("camera_tools.select_target_camera", text = "Camera")
		row.operator("camera_tools.select_movement_empty", text = "Empty")
		
		selectedTargets = getSelectedTargets(targetList)
		for target in selectedTargets:
			box = layout.box()
			box.label(target.parent.name + "  (" + str(targetList.index(target) + 1) + ")")
			box.prop(target, '["loading time"]', slider = False)
		
		if calculatedTargetAmount != getTargetAmount():
			layout.label("You should recalculate the animation", icon = 'ERROR')
		#layout.operator("camera_tools.dummy")

		
		
	
# operators
#############################
		
class AddTargetCamera(bpy.types.Operator):
	bl_idname = "camera_tools.insert_target_camera"
	bl_label = "Add Target Camera"
	
	@classmethod
	def poll(self, context):
		return not targetCameraExists()
		
	def execute(self, context):
		insertTargetCamera()
		return{"FINISHED"}
		
class SelectTargetCamera(bpy.types.Operator):
	bl_idname = "camera_tools.select_target_camera"
	bl_label = "Select Target Camera"
	
	def execute(self, context):
		selectTargetCamera()
		return{"FINISHED"}
		
class SelectMovementEmpty(bpy.types.Operator):
	bl_idname = "camera_tools.select_movement_empty"
	bl_label = "Select Movement Empty"
	
	def execute(self, context):
		selectMovementEmpty()
		return{"FINISHED"}
		
class SetupTargetObject(bpy.types.Operator):
	bl_idname = "camera_tools.new_target_object"
	bl_label = "New Targets From Selection"
	
	def execute(self, context):
		newTargets()
		return{"FINISHED"}
		
class DeleteTargetOperator(bpy.types.Operator):
	bl_idname = "camera_tools.delete_target"
	bl_label = "Delete Target"
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		deleteTarget(self.currentIndex)
		return{"FINISHED"}
		
class RecalculateAnimationOperator(bpy.types.Operator):
	bl_idname = "camera_tools.recalculate_animation"
	bl_label = "Recalculate Animation"
	
	def execute(self, context):
		createFullAnimation(getTargetList())
		return{"FINISHED"}
		
class MoveTargetUp(bpy.types.Operator):
	bl_idname = "camera_tools.move_target_up"
	bl_label = "Move Target Up"
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		moveTargetUp(self.currentIndex)
		return{"FINISHED"}
		
class MoveTargetDown(bpy.types.Operator):
	bl_idname = "camera_tools.move_target_down"
	bl_label = "Move Target Down"
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		moveTargetDown(self.currentIndex)
		return{"FINISHED"}		
		
class SelectTarget(bpy.types.Operator):
	bl_idname = "camera_tools.select_target"
	bl_label = "Select Target"
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		selectTarget(self.currentIndex)
		return{"FINISHED"}

class GoToNextTarget(bpy.types.Operator):		
	bl_idname = "camera_tools.go_to_next_target"
	bl_label = "Go To Next Target"
	
	def execute(self, context):
		goToNextTarget()
		return{"FINISHED"}
		
class GoToPreviousTarget(bpy.types.Operator):		
	bl_idname = "camera_tools.go_to_previous_target"
	bl_label = "Go To Previous Target"
	
	def execute(self, context):
		goToPreviousTarget()
		return{"FINISHED"}

class dummy(bpy.types.Operator):
	bl_idname = "camera_tools.dummy"
	bl_label = "dummy"
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		moveTargetUp(self.currentIndex)
		return{"FINISHED"}

		
# register
#############################

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)