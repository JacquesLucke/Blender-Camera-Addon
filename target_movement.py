import bpy, math
from utils import *

cameraRigPropertyName = "Camera Rig Type"
targetCameraType = "TARGET" 
deleteOnCleanup = "Delete on Cleanup"
autoAnimationType = "Auto Animation Type"
keyframeDistancePropertyName = "Keyframe Distance"

targetCameraName = "TARGET CAMERA"

useListSeparator = False

shouldRecalculate = False


# insert basic camera setup
#################################

def insertTargetMovementCamera():
	oldSelection = getSelectedObjects()

	camera = newCamera()
	movement = newMovementEmpty()
	
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
	setCustomProperty(camera, autoAnimationType, "full")
	setCustomProperty(camera, keyframeDistancePropertyName, 40, min = 1)
	return camera
	
def newMovementEmpty():
	movement = newEmpty(name = "Movement Empty", location = [0, 0, 0])
	movement.empty_draw_size = 0.2
	setCustomProperty(movement, "travel", 1.0, min = 1.0)
	return movement
	
	
# create animation
###########################

def recalculateAnimation():
	createFullAnimation(getTargetList())
	
def createFullAnimation(targetList):
	cleanupScene()
	if useFullAutoAnimation():  removeAnimation()

	movement = getMovementEmpty()
	deleteAllConstraints(movement)
	
	for target in targetList:
		setupTargetObject(target)
		
	createTravelToConstraintDrivers()
	
	if useFullAutoAnimation(): createTravelAnimation()
	else: movement["travel"] = 1.0
	
	shouldRecalculate = False
	
def cleanupScene():
	deselectAll()
	for object in bpy.context.scene.objects:
		if object.get(deleteOnCleanup) == "yes":
			object.select = True
			object.hide = False
				
	bpy.ops.object.delete()	
	
def removeAnimation():
	clearAnimation(getMovementEmpty(), '["travel"]')
		
def setupTargetObject(object):
	deselectAll()
	object.select = True
	setActive(object)
	bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
	center = newEmpty(name = "center")
	setParentWithoutInverse(center, object)
	setCustomProperty(center, deleteOnCleanup, "yes")
	createConstraintSet(center)
	
	center.hide = True
	
def createConstraintSet(target):
	movement = getMovementEmpty()
	locationConstraint = movement.constraints.new(type = "COPY_LOCATION")
	rotationConstraint = movement.constraints.new(type = "COPY_ROTATION")
	locationConstraint.target = target
	rotationConstraint.target = target
	locationConstraint.influence = 0
	rotationConstraint.influence = 0
	locationConstraint.show_expanded = False
	rotationConstraint.show_expanded = False
	
	driver = newDriver(movement, 'constraints["' + rotationConstraint.name + '"].influence')
	linkFloatPropertyToDriver(driver, "var", movement, 'constraints["' + locationConstraint.name + '"].influence')
	driver.expression = "var"
	
def createTravelToConstraintDrivers():
	movement = getMovementEmpty()
	constraints = movement.constraints
	
	for i in range(getTargetAmount()):
		constraint = constraints[i*2]
		driver = newDriver(movement, 'constraints["' + constraint.name + '"].influence')
		linkFloatPropertyToDriver(driver, "var", movement, '["travel"]')
		driver.expression = "var - " + str(i)
		
def createTravelAnimation():
	movement = getMovementEmpty()
	
	for i in range(getTargetAmount()):
		movement["travel"] = float(i + 1)
		movement.keyframe_insert(data_path='["travel"]', frame = i * getKeyframeDistance() + 1)
		
	slowAnimationOnEachKeyframe(movement, '["travel"]')


	
# animation operations
#############################

def useAutoTravelAnimation():
	camera = getTargetCamera()
	camera[autoAnimationType] = "full"
	recalculateAnimation()

def removeAutoTravelAnimation():
	camera = getTargetCamera()
	camera[autoAnimationType] = "no travel"
	
def smoothKeyframes():
	slowAnimationOnEachKeyframe(getMovementEmpty(), '["travel"]')
	
# target operations
#############################

def newTargets():
	targets = getTargetList()
	selectedObjects = []
	for object in getSelectedObjects():
		selectedObjects.append(object)
	selectedObjects.reverse()
	for object in selectedObjects:
		targets.append(object)
	createFullAnimation(targets)
	
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
	
	
# utilities
#############################

def targetCameraExists():
	if getTargetCamera() is None: return False
	else: return True
def getTargetCamera():
	return bpy.data.objects.get(targetCameraName)
def getMovementEmpty():
	return getTargetCamera().parent
			
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
	movement = getMovementEmpty()
	targets = []
	lastTarget = None
	for constraint in movement.constraints:
		targetEmpty = constraint.target
		if hasattr(targetEmpty, "parent"):
			if targetEmpty.parent is not None:
				if targetEmpty.parent != lastTarget:
					lastTarget = targetEmpty.parent
					targets.append(targetEmpty.parent)
	return targets

def useFullAutoAnimation():
	targetCamera = getTargetCamera()
	if targetCamera.get(autoAnimationType) == "full": return True
	else: return False
	
def getKeyframeDistance():
	return getTargetCamera().get(keyframeDistancePropertyName)
		

		
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
		
		fullAutoAnimation = useFullAutoAnimation()
		
		col = layout.column(align = True)
		recalculate = col.operator("camera_tools.recalculate_animation", text = "Recalculate")
			
		if fullAutoAnimation:
			col.prop(camera, '["' + keyframeDistancePropertyName + '"]', slider = False, text = "Frames per Text")
		else:
			col.operator("camera_tools.smooth_keyframes")
			
		row = col.row(align = True)
		if fullAutoAnimation: row.operator("camera_tools.remove_auto_travel_animation", text = "", icon = 'X')
		else: row.operator("camera_tools.use_auto_travel_animation", text = "", icon = 'ACTION')
		row.prop(movement, '["travel"]', text = "Travel", slider = False)
		
		box = layout.box()
		col = box.column(align = True)
		targetList = getTargetList()
		for i in range(len(targetList)):
			row = col.split(percentage=0.6, align = True)
			row.scale_y = 1.35
			name = row.operator("camera_tools.select_target", targetList[i].name)
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
		
		if shouldRecalculate: layout.label("You should recalculate the animation", icon = 'ERROR')
		
		#layout.operator("camera_tools.dummy")

		
		
	
# operators
#############################
		
class AddTargetMovementCamera(bpy.types.Operator):
	bl_idname = "camera_tools.add_target_movement_camera"
	bl_label = "Add Target Camera"
	
	@classmethod
	def poll(self, context):
		return not targetCameraExists()
		
	def execute(self, context):
		insertTargetMovementCamera()
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
		
class UseAutoTravelAnimation(bpy.types.Operator):
	bl_idname = "camera_tools.use_auto_travel_animation"
	bl_label = "Create Auto Travel animation"
	
	def execute(self, context):
		useAutoTravelAnimation()
		return{"FINISHED"}
		
class RemoveAutoTravelAnimation(bpy.types.Operator):
	bl_idname = "camera_tools.remove_auto_travel_animation"
	bl_label = "Remove Auto Travel animation"
	
	def execute(self, context):
		removeAutoTravelAnimation()
		return{"FINISHED"}
		
class SmoothKeyframes(bpy.types.Operator):
	bl_idname = "camera_tools.smooth_keyframes"
	bl_label = "Smooth Keyframes"
	
	def execute(self, context):
		smoothKeyframes()
		return{"FINISHED"}		
		
class SelectTarget(bpy.types.Operator):
	bl_idname = "camera_tools.select_target"
	bl_label = "Select Target"
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		selectTarget(self.currentIndex)
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