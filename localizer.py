import time
from utils import comment
from keras.models import load_model
import os
from PyQt5 import QtCore 
import cv2
import numpy as np
import tensorflow as tf
global graph
from PyQt5.QtWidgets import QApplication
import pickle
from sklearn.preprocessing import StandardScaler
graph = tf.get_default_graph()

experiment_folder_location = os.path.join(os.path.dirname(os.path.abspath(__file__)),'models')

class Localizer(QtCore.QObject):
	localizer_move_signal = QtCore.pyqtSignal('PyQt_PyObject','PyQt_PyObject','PyQt_PyObject','PyQt_PyObject')
	get_position_signal = QtCore.pyqtSignal()
	fire_qswitch_signal = QtCore.pyqtSignal()
	stop_laser_flash_signal = QtCore.pyqtSignal()
	ai_fire_qswitch_signal = QtCore.pyqtSignal()
	start_laser_flash_signal = QtCore.pyqtSignal()
	qswitch_screenshot_signal = QtCore.pyqtSignal()

	def __init__(self, parent = None):
		super(Localizer, self).__init__(parent)
		self.localizer_model = load_model(os.path.join(experiment_folder_location,'multiclass_localizer14.hdf5'))
		self.norm = StandardScaler()
		self.hallucination_img = cv2.imread(os.path.join(experiment_folder_location,'target___28_06_2018___15.16.37.613192.tif'))
		# self.localizer_model = load_model(os.path.join(experiment_folder_location,'binary_localizer6.hdf5'))
		self.localizer_model._make_predict_function()
		self.position = np.zeros((1,2))
		self.lysed_cell_count = 0
		self.get_well_center = True
		self.delay_time = .2
		# cv2.imshow('img',self.get_network_output(self.hallucination_img,'multi'))
	@QtCore.pyqtSlot('PyQt_PyObject')
	def vid_process_slot(self,image):
		self.image = image
		
	def get_network_output(self,img,mode):
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)		
		img = cv2.resize(img, (125, 125))
		img = self.norm.fit_transform(img)
		img = np.expand_dims(img,axis = 4) 
		img = np.expand_dims(img,axis = 0) 
		with graph.as_default():
			segmented_image = self.localizer_model.predict(img,batch_size = 1)	
		if mode == 'multi':
			print(segmented_image.shape)
			return_img = np.zeros((125,125,3))
			#red cell
			return_img[:,:,2] = segmented_image[0,:,:,1]			
			#green cell
			return_img[:,:,1] = segmented_image[0,:,:,2]			
		elif mode == 'binary':
			return_img = segmented_image
		return return_img

	# def continuous_extermination(self):
	# 	'''
	# 	function to run the network in a loop until everything on the screen 
	# 	is destroyed
	# 	'''
	# 	cell_found = True
	# 	while cell_found == True:

	@QtCore.pyqtSlot('PyQt_PyObject')
	def position_return_slot(self,position):
		# we need to get the position from the stage and store it
		self.position = position.copy()
		print('GOT POSITION!!!!!!!')
		self.wait_for_position = False

	def get_stage_position(self):		
		self.wait_for_position = True
		while self.wait_for_position == True:
			self.get_position_signal.emit()
			QApplication.processEvents()
			time.sleep(.1)
			print('waiting for position...')
		return self.position

	def move_frame(self,direction,relative=True):
		distance = 10
		frame_dir_dict = {
		'u': np.array([0,-distance]),
		'd': np.array([0,distance]),
		'l': np.array([-distance,0]),
		'r': np.array([distance,0])
		}
		self.localizer_move_signal.emit(frame_dir_dict[direction],False,True,False)


	def return_to_original_position(self,position):				
		self.localizer_move_signal.emit(position,False,False,False)

	@QtCore.pyqtSlot()
	def localize(self):
		'''
		function to scan an entire well, and lyse the number of cells desired by the user,
		using the method of lysis that the user selects, then returns to the original
		position (the center of the well)
		'''
		# first get our well center position
		well_center = self.get_stage_position()		
		# now start moving and lysing all in view
		self.lyse_all_in_view()
		box_size = 1
		directions = self.get_spiral_directions(box_size)		
		self.get_well_center = False
		for num,let in directions:
			for i in range(num):
				print('MOVING:',num,let)
				time.sleep(2)
				self.move_frame(let)				
				QApplication.processEvents()
				self.lyse_all_in_view()
		self.return_to_original_position(well_center)
		
	def get_spiral_directions(self,box_size):
	    letters = ['u', 'l', 'd', 'r']
	    nums = []
	    lets = []
	    for i in range(1,box_size*2,2):
	        num_line = [i]*2 + [i+1]*2
	        let_line = letters
	        nums += num_line
	        lets += let_line
	    nums += [nums[-1]]
	    lets += lets[-4]
	    directions = zip(nums,lets)
	    return directions			

	def delay(self):
		time.sleep(self.delay_time)

	def lyse_all_in_view(self):
		'''
		gets initial position lyses all cells in view, and then
		returns to initial position
		'''
		view_center = self.get_stage_position()
		self.start_laser_flash_signal.emit()
		print('lysing all in view...')
		self.delay()
		segmented_image = self.get_network_output(self.hallucination_img,'multi')
		cv2.imshow('Cell Outlines and Centers',segmented_image)
		# lyse all cells in view
		self.lyse_cells(segmented_image,'red','excision')
		# now return to our original position		
		self.delay()
		self.return_to_original_position(view_center)
		self.stop_laser_flash_signal.emit()	

	def lyse_cells(self,segmented_image,cell_type,lyse_type):
		'''
		takes the image from the net, and determines what targets to lyse
		based upon the input parameters. also lyses in different ways based
		upon the input parameters
		'''
		confidence_image = self.threshold_based_on_type(segmented_image,cell_type)

		cell_contours,cell_centers = self.get_contours_and_centers(confidence_image)

		if len(cell_centers) == 0:
			print('NO CELLS FOUND')
			return

		

		if lyse_type == 'direct':
			self.direct_lysis(cell_centers)
		elif lyse_type == 'excision':			
			self.excision_lysis(cell_contours)

	def excision_lysis(self,cell_contours):
		# for each contour we want to trace it
		window_center = np.array([125./2,125./2])
		for i in range(len(cell_contours)):			
			contour = cell_contours[i]
			point_number = contour.shape[0] 
			old_center = contour[0].reshape(2)
			self.hit_target(old_center-window_center,True)
			time.sleep(.2)
			for j in range(1,point_number):		
				new_center = contour[j].reshape(2)		
				move_vec = -old_center + new_center
				scaled_move_vec = move_vec*1.5
				self.hit_target(scaled_move_vec,False)
				old_center = new_center
				time.sleep(.2)		

	def direct_lysis(self,cell_centers):
		window_center = np.array([125./2,125./2])
		print('centers:',cell_centers)
		old_center = cell_centers[0]
		self.hit_target(old_center-window_center,True,'direct')
		self.delay()
		if len(cell_centers) > 1:
			for i in range(1,len(cell_centers)):
				self.hit_target(-old_center + cell_centers[i],False,'direct')
				old_center = cell_centers[i]
				self.delay()

	def get_contours_and_centers(self,confidence_image):
		_, contours, _ = cv2.findContours(np.uint8(confidence_image), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		cell_image = np.zeros((125,125))
		cell_contours = []
		cell_centers = []
		for contour in contours:
			print(cv2.contourArea(contour))
			if cv2.contourArea(contour) > 20:
				(x,y),radius = cv2.minEnclosingCircle(contour)
				center = (int(x),int(y))
				cell_contours.append(contour)				
				cv2.circle(cell_image,center,2 ,(255,0,0),-1)
				center = np.array(center)
				cell_centers.append(center)
		return cell_contours,cell_centers
				# print('contour:',contour,type(contour),contour.shape)
		# cv2.drawContours(cell_image, contours, -1, (255,255,255), 1)
		# cv2.imshow('Cell Outlines and Centers',cell_image)

	def threshold_based_on_type(self,segmented_image,cell_type):
		if cell_type == 'green':
			_,confidence_image = cv2.threshold(segmented_image[:,:,1],.5,1,cv2.THRESH_BINARY)
		elif cell_type == 'red':
			_,confidence_image = cv2.threshold(segmented_image[:,:,2],.5,1,cv2.THRESH_BINARY)
		elif cell_type == 'any':
			# assumes a binary image!
			_,confidence_image = cv2.threshold(segmented_image,.5,1,cv2.THRESH_BINARY)
		return confidence_image

	def hit_target(self,center,goto_reticle = False,lysis_type = 'direct'):
		# we need to scale our centers up to the proper resolution and then 
		# send it to the stage
		# localizer_move_slot(self, move_vector, goto_reticle = False,move_relative = True,scale_vector = True):
		x = center[0]*851/125
		y = center[1]*681/125
		if lysis_type == 'direct':		
			self.localizer_move_signal.emit(np.array([x,y]),goto_reticle,True,True)
		elif lysis_type == 'excision':
			self.localizer_move_signal.emit(np.array([x,y]),goto_reticle,True,True)
		self.ai_fire_qswitch_signal.emit()
		# for i in range(1):
			# self.ai_fire_qswitch_signal.emit()
		# 	time.sleep(.1)
		
		# for i in range(num_shots):
		# 	time.sleep(.1)
		# 	self.fire_qswitch_signal.emit()

				




	@QtCore.pyqtSlot()
	def localize2(self):
		self.start_laser_flash_signal.emit()
		# segmented_image = self.get_network_output(self.image,'binary')
		segmented_image = self.get_network_output(self.image,'multi')
		# print(segmented_image.shape)
		# segmented_image = np.argmax(segmented_image,axis = 2)
		# print(segmented_image.shape)
		cv2.imshow('Cell Outlines and Centers',segmented_image)
		# this retrieves the green cells
		# _,confidence_image = cv2.threshold(segmented_image[:,:,1],.5,1,cv2.THRESH_BINARY)
		# # binary localization 
		# # _,confidence_image = cv2.threshold(segmented_image,.5,1,cv2.THRESH_BINARY)
		# _, contours, _ = cv2.findContours(np.uint8(confidence_image), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		# cell_image = np.zeros((125,125))
		# cell_contours = []
		# cell_centers = []
		# for contour in contours:
		# 	print(cv2.contourArea(contour))
		# 	if cv2.contourArea(contour) > 20:
		# 		(x,y),radius = cv2.minEnclosingCircle(contour)
		# 		center = (int(x),int(y))
		# 		cell_contours.append(contour)				
		# 		cv2.circle(cell_image,center,2 ,(255,0,0),-1)
		# 		center = np.array(center)
		# 		cell_centers.append(center)
		# 		# print('contour:',contour,type(contour),contour.shape)
		# cv2.drawContours(cell_image, contours, -1, (255,255,255), 1)
		# cv2.imshow('Cell Outlines and Centers',cell_image)
		######## DIRECT SHOT LYSIS
		# if len(cell_centers) != 0:			
		# 	print('centers:',cell_centers)
		# 	window_center = np.array([125./2,125./2])
		# 	old_center = cell_centers[0]
		# 	self.hit_target(old_center-window_center,True)
		# 	time.sleep(.25)
		# 	if len(cell_centers) > 1:
		# 		for i in range(1,len(cell_centers)):
		# 			self.hit_target(-old_center + cell_centers[i])
		# 			old_center = cell_centers[i]
		# 			time.sleep(.25)			
		# else:
		# 	print('no cells found!')
		######### EXCISION
		# if len(cell_contours) != 0:			
		# 	window_center = np.array([125./2,125./2])
		# 	# for each contour we want to trace it
		# 	for i in range(len(contours)):			
		# 		contour = contours[i]
		# 		point_number = contour.shape[0] 
		# 		old_center = contour[0].reshape(2)
		# 		self.hit_target(old_center-window_center,True)
		# 		time.sleep(.25)
		# 		for j in range(1,point_number):		
		# 			new_center = contour[j].reshape(2)		
		# 			move_vec = -old_center + new_center
		# 			scaled_move_vec = move_vec*1.5
		# 			self.hit_target(scaled_move_vec)
		# 			old_center = new_center
		# 			time.sleep(.25)			
		# else:
		# 	print('no cells found!')
		self.stop_laser_flash_signal.emit()	

	

