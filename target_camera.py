'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy, math
from utils import *

targetCameraName = "TARGET CAMERA"
movementEmptyName = "MOVEMENT"
dataEmptyName = "TARGET CAMERA CONTAINER"
strongWiggleEmptyName = "STRONG WIGGLE"
wiggleEmptyName = "WIGGLE"
distanceEmptyName = "DISTANCE"
realTargetPrefix = "REAL TARGET"
partOfTargetCamera = "part of target camera"

useListSeparator = False

calculatedTargetAmount = 0
oldWiggleScale = 3
shouldRecalculate = False


# insert basic camera setup
#################################

def insertTargetCamera():
	oldSelection = getSelectedObjects()
	removeOldTargetCameraObjects()

	camera = newCamera()
	movement = newMovementEmpty()
	distanceEmpty = newDistanceEmpty()
	strongWiggle = newStrongWiggleEmpty()
	wiggle = newWiggleEmpty()
	dataEmpty = newDataEmpty()
	
	movement.parent = dataEmpty
	distanceEmpty.parent = movement
	strongWiggle.parent = distanceEmpty
	wiggle.parent = distanceEmpty
	camera.parent = wiggle;
	
	distanceEmpty.location.z = 4
	
	setActive(camera)
	bpy.context.object.data.dof_object = movement
	
	insertWiggleConstraint(wiggle, strongWiggle, dataEmpty)
	
	setSelectedObjects(oldSelection)
	newTargets()
	
def removeOldTargetCameraObjects():
	for object in bpy.data.objects:
		if isPartOfTargetCamera(object):
			delete(object)
	
def newCamera():
	bpy.ops.object.camera_add(location = [0, 0, 0])
	camera = bpy.context.object
	camera.name = targetCameraName
	camera.rotation_euler = [0, 0, 0]
	makePartOfTargetCamera(camera)
	bpy.context.scene.camera = camera
	return camera
	
def newMovementEmpty():
	movement = newEmpty(name = movementEmptyName, location = [0, 0, 0])
	movement.empty_draw_size = 0.2
	makePartOfTargetCamera(movement)
	movement.hide = True
	return movement
	
def newDistanceEmpty():
	distanceEmpty = newEmpty(name = distanceEmptyName, location = [0, 0, 0])
	distanceEmpty.empty_draw_size = 0.2
	makePartOfTargetCamera(distanceEmpty)
	distanceEmpty.hide = True
	return distanceEmpty

def newStrongWiggleEmpty():
	strongWiggle = newEmpty(name = strongWiggleEmptyName, location = [0, 0, 0])
	strongWiggle.empty_draw_size = 0.2
	makePartOfTargetCamera(strongWiggle)
	strongWiggle.hide = True
	return strongWiggle
	
def newWiggleEmpty():
	wiggle = newEmpty(name = wiggleEmptyName, location = [0, 0, 0])
	wiggle.empty_draw_size = 0.2
	makePartOfTargetCamera(wiggle)
	wiggle.hide = True
	return wiggle

def newDataEmpty():
	dataEmpty = newEmpty(name = dataEmptyName, location = [0, 0, 0])
	setCustomProperty(dataEmpty, "travel", 1.0, min = 1.0)
	setCustomProperty(dataEmpty, "stops", [])
	setCustomProperty(dataEmpty, "wiggle strength", 0.0, min = 0.0, max = 1.0)
	setCustomProperty(dataEmpty, "wiggle scale", 5.0, min = 0.0)
	dataEmpty.hide = True
	lockCurrentTransforms(dataEmpty)
	makePartOfTargetCamera(dataEmpty)
	return dataEmpty

def insertWiggleConstraint(wiggle, strongWiggle, dataEmpty):
	constraint = wiggle.constraints.new(type = "COPY_TRANSFORMS")
	constraint.target = strongWiggle
	driver = newDriver(wiggle, 'constraints["' + constraint.name + '"].influence')
	linkFloatPropertyToDriver(driver, "var", dataEmpty, '["wiggle strength"]')	
	driver.expression = "var**2"
	
# create animation
###########################

def recalculateAnimation():
	createFullAnimation(getTargetList())
	
def createFullAnimation(targetList):
	global calculatedTargetAmount, shouldRecalculate
	cleanupScene(targetList)
	removeAnimation()

	movement = getMovementEmpty()
	dataEmpty = getDataEmpty()
	deleteAllConstraints(movement)
	
	createWiggleModifiers()
	
	for target in targetList:
		createConstraintSet(target)
		
	createTravelToConstraintDrivers()
	createTravelAnimation(targetList)
	calculatedTargetAmount = getTargetAmount()
	
	shouldRecalculate = False
	
def cleanupScene(targetList):
	deselectAll()
	for object in bpy.context.scene.objects:
		if isTargetName(object.name) and object not in targetList:
			object.select = True
			object.hide = False
	bpy.ops.object.delete()	
	
def removeAnimation():
	clearAnimation(getDataEmpty(), '["travel"]')
	
def createWiggleModifiers():
	global oldWiggleScale
	strongWiggle = getStrongWiggle()
	dataEmpty = getDataEmpty()
	wiggleScale = getWiggleScale(dataEmpty)
	clearAnimation(strongWiggle, "location")
	strongWiggle.location = [0, 0, 0]
	insertWiggle(strongWiggle, "location", 6, wiggleScale)
	oldWiggleScale = wiggleScale
	
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
		
def createTravelAnimation(targetList):
	dataEmpty = getDataEmpty()
	stops = []
	
	frame = 0
	for i in range(getTargetAmount()):
		frame += getLoadingTime(targetList[i])
		dataEmpty["travel"] = float(i + 1)
		dataEmpty.keyframe_insert(data_path='["travel"]', frame = frame)
		stops.append(frame)
		
		frame += getStayTime(targetList[i])
		dataEmpty["travel"] = float(i + 1)
		dataEmpty.keyframe_insert(data_path='["travel"]', frame = frame)
		
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

	empty = newEmpty(name = realTargetPrefix, location = [0, 0, 0])
	empty.empty_draw_size = 0.4
	setParentWithoutInverse(empty, target)
	
	setCustomProperty(empty, "loading time", 20, min = 1)
	setCustomProperty(empty, "stay time", 20, min = 0)
	
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
	return bpy.data.objects.get(movementEmptyName)
def getDataEmpty():
	return bpy.data.objects.get(dataEmptyName)
def getStrongWiggle():
	return bpy.data.objects.get(strongWiggleEmptyName)
			
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
	return name[:len(realTargetPrefix)] == realTargetPrefix
	
def getKeyframeDistance():
	return getTargetCamera().get(keyframeDistancePropertyName)
	
def getSelectedTargets(targetList):
	objects = getSelectedObjects()
	targets = []
	for object in objects:
		targetsOfObject = getTargetsFromObject(object, targetList)
		for target in targetsOfObject:
			if target not in targets:
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
	
def getLoadingTime(target):
	return target["loading time"]
	
def getStayTime(target):
	return target["stay time"]
	
def getWiggleScale(dataEmpty):
	return dataEmpty["wiggle scale"]
	
def makePartOfTargetCamera(object):
	object[partOfTargetCamera] = "1"
	
def isPartOfTargetCamera(object):
	if object.get(partOfTargetCamera) is None:
		return False
	return True

		
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
		global shouldRecalculate
		
		layout = self.layout
		
		camera = getTargetCamera()
		movement = getMovementEmpty()
		dataEmpty = getDataEmpty()
		targetList = getTargetList()
		
		layout.operator("camera_tools.recalculate_animation", text = "Recalculate")
			
		row = layout.row(align = True)
		row.operator("camera_tools.go_to_previous_target", icon = 'TRIA_LEFT', text = "")
		row.label("Travel: " + str(getTravelValue()))
		row.operator("camera_tools.go_to_next_target", icon = 'TRIA_RIGHT', text = "")
		
		box = layout.box()
		col = box.column(align = True)
		
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
		
		selectedTargets = getSelectedTargets(targetList)
		for target in selectedTargets:
			box = layout.box()
			box.label(target.parent.name + "  (" + str(targetList.index(target) + 1) + ")")
			
			col = box.column(align = True)
			col.prop(target, '["loading time"]', slider = False, text = "Loading Time")
			col.prop(target, '["stay time"]', slider = False, text = "Time to Stay")
			
		col = layout.column(align = True)
		col.label("Wiggle")
		col.prop(dataEmpty, '["wiggle strength"]', text = "Strength")
		col.prop(dataEmpty, '["wiggle scale"]', text = "Scale")
		
		if calculatedTargetAmount != getTargetAmount(): shouldRecalculate = True
		if oldWiggleScale != getWiggleScale(dataEmpty): shouldRecalculate = True
		
		if shouldRecalculate:
			layout.label("You should recalculate the animation", icon = 'ERROR')

		
		
	
# operators
#############################
		
class AddTargetCamera(bpy.types.Operator):
	bl_idname = "camera_tools.insert_target_camera"
	bl_label = "Add Target Camera"
	bl_description = "Create new active camera and create targets from selection."
	
	@classmethod
	def poll(self, context):
		return not targetCameraExists()
		
	def execute(self, context):
		insertTargetCamera()
		return{"FINISHED"}
		
class SetupTargetObject(bpy.types.Operator):
	bl_idname = "camera_tools.new_target_object"
	bl_label = "New Targets From Selection"
	bl_description = "Use selected objects as targets."
	
	def execute(self, context):
		newTargets()
		return{"FINISHED"}
		
class DeleteTargetOperator(bpy.types.Operator):
	bl_idname = "camera_tools.delete_target"
	bl_label = "Delete Target"
	bl_description = "Delete the target from the list."
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		deleteTarget(self.currentIndex)
		return{"FINISHED"}
		
class RecalculateAnimationOperator(bpy.types.Operator):
	bl_idname = "camera_tools.recalculate_animation"
	bl_label = "Recalculate Animation"
	bl_description = "Regenerates most of the constraints, drivers and keyframes."
	
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
	bl_description = "Select that target."
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		selectTarget(self.currentIndex)
		return{"FINISHED"}

class GoToNextTarget(bpy.types.Operator):		
	bl_idname = "camera_tools.go_to_next_target"
	bl_label = "Go To Next Target"
	bl_description = "Change frame to show next target."
	
	def execute(self, context):
		goToNextTarget()
		return{"FINISHED"}
		
class GoToPreviousTarget(bpy.types.Operator):		
	bl_idname = "camera_tools.go_to_previous_target"
	bl_label = "Go To Previous Target"
	bl_description = "Change frame to show previous target."
	
	def execute(self, context):
		goToPreviousTarget()
		return{"FINISHED"}

		
# register
#############################

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)