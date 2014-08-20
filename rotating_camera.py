import bpy
from utils import *

cameraRigPropertyName = "Camera Rig Type"

settingsObjectPropertyName = "Settings Object"
mainControlerPropertyName = "Main Controler"
targetControlerPropertyName = "Target Controler"
positionControlerPropertyName = "Position Controler"
cameraPropertyName = "Camera"

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
	setCustomProperty(mainControler, settingsObjectPropertyName, settingsObjectName)
	setCustomProperty(targetControler, settingsObjectPropertyName, settingsObjectName)
	setCustomProperty(positionControler, settingsObjectPropertyName, settingsObjectName)
	setCustomProperty(rotationControler, settingsObjectPropertyName, settingsObjectName)
	setCustomProperty(camera, settingsObjectPropertyName, settingsObjectName)
	
	setCustomProperty(rotationControler, mainControlerPropertyName, mainControler.name)
	setCustomProperty(rotationControler, targetControlerPropertyName, targetControler.name)
	setCustomProperty(rotationControler, positionControlerPropertyName, positionControler.name)
	setCustomProperty(rotationControler, cameraPropertyName, camera.name)
	
	mainControler.show_x_ray = True
	targetControler.show_x_ray = True
	
	deselectAll()
	mainControler.select = True

	
	
	
def getCurrentSettingsObjectOrNothing():
	activeObject = bpy.context.active_object
	if isPartOfRotatingCamera(activeObject):
		return bpy.data.objects[activeObject[settingsObjectPropertyName]]
	
def isPartOfRotatingCamera(object):
	if object:
		if settingsObjectPropertyName in object:
			return True
	return False
	
	
def insertTimeBasedRotationAnimation():
	settingsObject = getCurrentSettingsObjectOrNothing()
	if settingsObject:
		driver = newDriver(settingsObject, '["rotationProgress"]')
		driver.expression = "frame / 100"
		
def selectTargetControler():
	settingsObject = getCurrentSettingsObjectOrNothing()
	if settingsObject:
		deselectAll()
		bpy.data.objects[settingsObject[targetControlerPropertyName]].select = True
		
def selectMainControler():
	settingsObject = getCurrentSettingsObjectOrNothing()
	if settingsObject:
		deselectAll()
		bpy.data.objects[settingsObject[mainControlerPropertyName]].select = True
		
def selectPositionControler():
	settingsObject = getCurrentSettingsObjectOrNothing()
	if settingsObject:
		deselectAll()
		bpy.data.objects[settingsObject[positionControlerPropertyName]].select = True
		
def selectCamera():
	settingsObject = getCurrentSettingsObjectOrNothing()
	if settingsObject:
		deselectAll()
		bpy.data.objects[settingsObject[cameraPropertyName]].select = True
		
		
		
		
		
# interface	

class CameraSettingsPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Animation"
	bl_label = "Camera Settings"
	bl_context = "objectmode"
	
	@classmethod
	def poll(self, context):
		return getCurrentSettingsObjectOrNothing()
	
	def draw(self, context):
		layout = self.layout
		
		settingsObject = getCurrentSettingsObjectOrNothing()
		if settingsObject:  
			col = layout.column(align = True)
			col.label("Select")
			row = col.row(align = True)
			row.operator("animation.select_main_controler", text = "Main")
			row.operator("animation.select_target_controler", text = "Target")
			row = col.row(align = True)
			row.operator("animation.select_position_controler", text = "Circle")
			row.operator("animation.select_camera", text = "Camera")
			
			col = layout.column(align = True)
			col.operator("animation.insert_time_rotation_animation")
			col.prop(settingsObject, '["rotationProgress"]', text = "Rotations", slider = False)
		
		
# operators
		
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
		
class SelectTargetControlerOperator(bpy.types.Operator):
	bl_idname = "animation.select_target_controler"
	bl_label = "Select Target"
	
	def execute(self, context):
		selectTargetControler()
		return{"FINISHED"}
		
class SelectMainControlerOperator(bpy.types.Operator):
	bl_idname = "animation.select_main_controler"
	bl_label = "Select Main"
	
	def execute(self, context):
		selectMainControler()
		return{"FINISHED"}
		
class SelectPositionControlerOperator(bpy.types.Operator):
	bl_idname = "animation.select_position_controler"
	bl_label = "Select Circle"
	
	def execute(self, context):
		selectPositionControler()
		return{"FINISHED"}
		
class SelectCameraOperator(bpy.types.Operator):
	bl_idname = "animation.select_camera"
	bl_label = "Select Camera"
	
	def execute(self, context):
		selectCamera()
		return{"FINISHED"}
		
		
		
		
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)
		
	