from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *
import time
from utils import comment
import matplotlib.pyplot as plt
from PyQt5 import QtCore
import threading,cv2,time
from PyQt5.QtWidgets import QApplication
from multiprocessing.pool import ThreadPool
import numpy as np
import os
from utils import now


class autofocuser(QtCore.QObject):
	'''
	assumes that the stage is maxed out in the CCW direction at start
	which is the maxed out negative direction. therefore any of our
	steps in the positive direction will cause us to move from the 
	max position of the focus
	'''
	# TODO implement a property that prevents the motor from ever going outside of its range. 
	position_and_variance_signal = QtCore.pyqtSignal('PyQt_PyObject')
	def __init__(self, parent = None):
		super(autofocuser, self).__init__(parent)
		self.ch = Stepper()
		self.ch.openWaitForAttachment(5000)
		self.ch.setEngaged(True)
		self.full_scale = 27300
		self.image_count = 0
		self.track_position = False
		self.pool = ThreadPool(processes=3)
		self.velocity = 0
		self.ch.setDataInterval(100)
		self.position = 0
		self.focused_position = 0
		self.status_dict = {'current limit':self.ch.getCurrentLimit,
				'control mode': self.ch.getControlMode,
				# 'setting min position: ': self.ch.setMinPosition(0),
				'min position': self.ch.getMinPosition,
				# 'setting max position: ': self.ch.setMaxPosition(self.full_scale),
				'max position': self.ch.getMaxPosition,
				'rescale factor': self.ch.getRescaleFactor,
				'target position': self.ch.getTargetPosition,
				'acceleration': self.ch.getAcceleration,
				'engaged?': self.ch.getEngaged,
				'max velocity:': self.ch.getMaxVelocityLimit,
				'data interval': self.ch.getDataInterval,
				'min data interval': self.ch.getMinDataInterval}

		for k,v in self.status_dict.items():
				comment('{}: {}'.format(k,v()))	
		self.ch.setOnVelocityChangeHandler(self.velocity_change_handler)
		self.ch.setOnPositionChangeHandler(self.position_change_handler)
		self.image_title = 0
		# self.step_to_position(self.full_scale)
		# self.autofocus()

	def velocity_change_handler(self,self2,velocity):
		# print('VELOCITY CHANGED:',velocity)
		self.velocity = velocity

	def position_change_handler(self,self2,position):
		# print('POSITION CHANGED:',position)
		self.position = position

	@QtCore.pyqtSlot('PyQt_PyObject')
	def vid_process_slot(self,image):
		self.image = image
		# print(image.shape)
		self.image_count += 1
		# print('image received in autofocus')

	def get_position(self):
		self.position = self.ch.getPosition()
		comment('stepper position: {}'.format(self.position))
		return self.position

	def step_to_relative_position(self,position):
		self.ch.setAcceleration(10000)
		self.ch.setVelocityLimit(10000)	
		# TODO check if the given position will make us exceed the range		
		self.ch.setTargetPosition(self.position + position)
		self.position += position

	def roll_forward(self):
		self.ch.setControlMode(1)
		self.ch.setAcceleration(15000)
		self.ch.setVelocityLimit(-2000)		

	def roll_backward(self):
		self.ch.setControlMode(1)
		self.ch.setAcceleration(15000)
		self.ch.setVelocityLimit(2000)

	def stop_roll(self):
		self.ch.setVelocityLimit(0)
		self.ch.setControlMode(0)
		self.ch.setAcceleration(10000)
		# comment('focus at {} steps'.format(self.get_position()))

	def swing_range(self):
		self.ch.setVelocityLimit(2000)
		self.ch.setTargetPosition(-self.full_scale+2500)

	def retract_objective(self):
		self.focused_position = self.get_position()
		self.step_to_relative_position(-70000)
		while self.ch.getIsMoving() == True: time.sleep(.1)
		return True

	def return_objective_to_focus(self):
		self.ch.setTargetPosition(self.focused_position)

	@QtCore.pyqtSlot()
	def autofocus(self):
		range = 2000
		variance1, location1, variances1 = self.focus_over_range(range)
		self.step_to_relative_position(-range)
		variance2, location2, variances2 = self.focus_over_range(-range)
		variances2.reverse()
		total_variances = variances2 + variances1
		self.position_and_variance_signal.emit(([],total_variances))
		if variance1 > variance2:
			self.ch.setTargetPosition(location1)
		elif variance2 > variance1:
			self.ch.setTargetPosition(location2)
		while self.ch.getIsMoving() == True:
			time.sleep(.1)		

	def focus_over_range(self,range):
		self.pool.apply_async(self.step_to_relative_position(range))		
		variances = []
		positions = []
		old_position = 0
		self.image_title += 1
		self.ch.setAcceleration(15000)
		self.ch.setVelocityLimit(2000)
		while self.ch.getIsMoving() == True:
			QApplication.processEvents() 
			new_position = self.position
			if old_position != new_position: positions.append(self.position)
			old_position = new_position
			# we want to focus on what's towards the center of our image
			h,w = self.image.shape[0],self.image.shape[1]
			img = self.image[int(.25*h):int(.75*h),int(.25*w):int(.75*w)]
			variance = cv2.Laplacian(img, cv2.CV_64F).var()
			variances.append(variance)		
			# print(os.path.join(experiment_folder_location,
			# 	'{}___{}.tif'.format(self.image_title,now())))
			# cv2.imwrite(os.path.join(experiment_folder_location,
			# 	'{}___{}.tif'.format(self.image_title,now())),self.image)	
		unit_scaled_location_of_highest_variance = variances.index(max(variances))/len(variances)
		print('location of highest variance: {}'.format(unit_scaled_location_of_highest_variance))
		closest_position = int(np.rint(len(positions)*unit_scaled_location_of_highest_variance))-1
		print('closest_position',closest_position)
		print('max variance of {} occurred at location {}'.format(
			max(variances),positions[closest_position]))
		# self.ch.setTargetPosition(positions[closest_position])
		# self.position_and_variance_signal.emit((positions,variances))
		while self.ch.getIsMoving() == True:
			time.sleep(.1)		
		

		return max(variances),positions[closest_position],variances

experiment_folder_location = os.path.join(os.path.dirname(os.path.abspath(__file__)),'Autofocus_data')
print(experiment_folder_location)
if __name__ == '__main__':
	a = autofocuser()
	a.autofocus()

