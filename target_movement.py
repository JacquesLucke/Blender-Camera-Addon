import bpy
from utils import *

def insertTargetMovementCamera():
	camera = newCamera()
	movement = newEmpty(name = "Movement Empty", location = [1, 1, 1])
	
	setParentWithoutInverse(camera, movement)
	camera.location.z = 4

def newCamera():
	bpy.ops.object.camera_add(location = [0, 0, 0])
	camera = bpy.context.object
	camera.name = "Target Camera"
	camera.rotation_euler = [0, 0, 0]
	return camera


# operators
		
class AddTargetMovementCamera(bpy.types.Operator):
	bl_idname = "animation.add_target_movement_camera"
	bl_label = "Add Target Camera"
	
	def execute(self, context):
		insertTargetMovementCamera()
		return{"FINISHED"}


def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)