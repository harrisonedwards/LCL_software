import time
from utils import comment,now
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
from utils import MeanIoU
from keras import backend as K
graph = tf.get_default_graph()
import skimage.transform as transform

num_classes = 3
miou_metric = MeanIoU(num_classes)
mean_iou = miou_metric.mean_iou

experiment_folder_location = os.path.join(os.path.dirname(os.path.abspath(__file__)),'models')

class wellStitcher():

	def __init__(self,box_size,initial_img):
		# get our inital coordinates
		self.box_size = int(box_size*2 + 1)
		self.center = int(np.ceil(box_size/2)+2)
		self.curr_x = self.center
		self.curr_y = self.center
		# initialize the image and show it
		self.img_x,self.img_y = int(1024),int(822)
		self.well_img = np.zeros((self.img_y*self.box_size,self.img_x*self.box_size,3))		
		self.stitch_img(initial_img)

	def manage_zoom(self,pos):
		print('trackbar at',pos)

	def stitch_img(self,img):
		self.well_img[self.curr_y*self.img_y:(self.curr_y+1)*self.img_y, self.curr_x*self.img_x:(self.curr_x+1)*self.img_x,:] = img
		self.resized_img = cv2.resize(self.well_img,(int(1024*.8),int(822*.8)),interpolation = cv2.INTER_AREA)
		cv2.imshow('Stitch',self.resized_img)		

	def add_img(self,let,img):
		if let == 'u': self.curr_y -= 1
		if let == 'd': self.curr_y += 1
		if let == 'l': self.curr_x -= 1
		if let == 'r': self.curr_x += 1
		print(self.curr_y,self.curr_x)
		self.stitch_img(img)

	def write_well_img(self):
		experiment_folder_location = os.path.join(os.path.dirname(os.path.abspath(__file__)),'well_images')
		cv2.imwrite(os.path.join(experiment_folder_location,
				'{}___{}.tif'.format('well_image',now())),self.well_img)
		cv2.createTrackbar('Zoom (2^x)','Stitch',1,6,self.manage_zoom)

class Localizer(QtCore.QObject):
	localizer_move_signal = QtCore.pyqtSignal('PyQt_PyObject','PyQt_PyObject','PyQt_PyObject','PyQt_PyObject')
	get_position_signal = QtCore.pyqtSignal()
	fire_qswitch_signal = QtCore.pyqtSignal()
	stop_laser_flash_signal = QtCore.pyqtSignal()
	ai_fire_qswitch_signal = QtCore.pyqtSignal('PyQt_PyObject')
	start_laser_flash_signal = QtCore.pyqtSignal()
	qswitch_screenshot_signal = QtCore.pyqtSignal('PyQt_PyObject')

	def __init__(self, parent = None):
		super(Localizer, self).__init__(parent)		
		# self.localizer_model = load_model(os.path.join(experiment_folder_location,'multiclass_localizer18_2.hdf5'),custom_objects={'mean_iou': mean_iou})
		self.localizer_model = load_model(os.path.join(experiment_folder_location,'model2018-10-18_08_47'),custom_objects={'mean_iou': mean_iou})
		self.norm = StandardScaler()		
		self.localizer_model._make_predict_function()
		self.position = np.zeros((1,2))
		self.well_center = np.zeros((1,2))
		self.lysed_cell_count = 0
		self.get_well_center = True
		self.delay_time = .35
		self.cells_to_lyse = 1
		self.cell_type_to_lyse = 'red'
		self.lysis_mode = 'direct'
		self.auto_lysis = False		

		# self.hallucination_img = cv2.imread(os.path.join(experiment_folder_location,'before_qswitch___06_07_2018___11.48.59.274395.tif'))
		# img = self.get_network_output(self.hallucination_img,'binary')
		# print('IMG SHAPE:',img.shape)
		# cv2.imshow('img',img)

	def stop_auto_lysis(self):
		self.auto_lysis = False

	def change_type_to_lyse(self,index):
		map_dict = {
		# 0:('red','multiclass_localizer18_2.hdf5'),
		# 1:('green','multiclass_localizer18_2.hdf5'),
		0:('red','model2018-10-18_08_47'),
		1:('green','model2018-10-18_08_47'),
		2:('green hope','second_binary_green_hope_localizer_16_0.28892_1_54_7_12.hdf5')
		}
		self.cell_type_to_lyse = map_dict[index][0]
		comment('loading cell localizer model...{}'.format(map_dict[index][1]))
		self.localizer_model = None
		K.clear_session()	
		# TODO: remove this if statement once we have a model that doesnt need the custom object
		if map_dict[index] != 'green hope':	
			self.localizer_model = load_model(os.path.join(experiment_folder_location,map_dict[index][1]),custom_objects={'mean_iou': mean_iou})
		else:
			self.localizer_model = load_model(os.path.join(experiment_folder_location,map_dict[index][1]))
		self.localizer_model._make_predict_function()
		comment('changed cell type to:'+str(self.cell_type_to_lyse))

	def change_lysis_mode(self,index):
		map_dict = {
		0:'direct',
		1:'excision'
		}
		self.lysis_mode = map_dict[index]
		comment('changed cell type to:' + str(self.lysis_mode))

	def set_cells_to_lyse(self,number_of_cells):
		self.cells_to_lyse = number_of_cells
		comment('set number of cells to lyse to:' + str(number_of_cells))

	@QtCore.pyqtSlot('PyQt_PyObject')
	def vid_process_slot(self,image):
		self.image = image
		
	def get_network_output(self,img,mode):
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)		
		img = transform.resize(img, (128, 128), anti_aliasing=False)
		img = self.norm.fit_transform(img)
		img = np.expand_dims(img,axis = 4) 
		img = np.expand_dims(img,axis = 0) 
		with graph.as_default():
			segmented_image = self.localizer_model.predict(img,batch_size = 1)	
		if mode == 'multi':
			# print(segmented_image.shape)
			return_img = np.zeros((128,128,3))
			#red cell
			return_img[:,:,2] = segmented_image[0,:,:,2]			
			#green cell
			return_img[:,:,1] = segmented_image[0,:,:,1]			
		elif mode == 'binary':
			return_img = segmented_image[0,:,:,0]
		return_img = transform.resize(return_img, (125, 125), anti_aliasing=False)
		return return_img

	@QtCore.pyqtSlot('PyQt_PyObject')
	def position_return_slot(self,position):
		# we need to get the position from the stage and store it
		self.position = position.copy()
		self.wait_for_position = False

	def get_stage_position(self):		
		self.wait_for_position = True
		while self.wait_for_position == True:
			self.get_position_signal.emit()
			QApplication.processEvents()
			time.sleep(.1)
		return self.position

	def move_frame(self,direction,relative=True):
		y_distance = 95
		x_distance = 120
		frame_dir_dict = {
		'u': np.array([0,-y_distance]),
		'd': np.array([0,y_distance]),
		'l': np.array([-x_distance,0]),
		'r': np.array([x_distance,0])
		}
		self.localizer_move_signal.emit(frame_dir_dict[direction],False,True,False)

	def return_to_original_position(self,position):				
		self.localizer_move_signal.emit(position,False,False,False)

	@QtCore.pyqtSlot()
	def localize2(self):
		box_size = 5
		self.well_center = self.get_stage_position()		
		stitcher = wellStitcher(box_size,self.image)		
		directions = self.get_spiral_directions(box_size)	
		for num,let in directions:
			self.delay()
			self.move_frame(let)				
			self.delay()
			QApplication.processEvents()
			stitcher.add_img(let,self.image)
		comment('writing well tile file...')
		stitcher.write_well_img()
		comment('tiling completed!')			

	@QtCore.pyqtSlot()
	def localize(self):
		'''
		function to scan an entire well, and lyse the number of cells desired by the user,
		using the method of lysis that the user selects, then returns to the original
		position (the center of the well)
		'''
		# first get our well center position		
		self.lysed_cell_count = 0
		self.auto_lysis = True
		self.well_center = self.get_stage_position()		
		# now start moving and lysing all in view
		self.lyse_all_in_view()
		box_size = 5
		# stitcher = wellStitcher(box_size,self.image)		
		directions = self.get_spiral_directions(box_size)		
		self.get_well_center = False
		for num,let in directions:
			for i in range(num):
				if self.auto_lysis == False:
					self.stop_laser_flash_signal.emit()	
					return
				if self.lysed_cell_count >= self.cells_to_lyse: 
					self.delay()
					self.return_to_original_position(self.well_center)
					return	
				self.delay()
				self.move_frame(let)				
				self.delay()
				QApplication.processEvents()
				self.delay()
				QApplication.processEvents()
				# stitcher.add_img(let,self.image)
				self.lyse_all_in_view()
		comment('lysis completed!')
		# stitcher.write_well_img()
		self.return_to_original_position(self.well_center)


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
		self.start_laser_flash_signal.emit()
		view_center = self.get_stage_position()		
		print('lysing all in view...')
		self.delay()
		if self.cell_type_to_lyse == 'green hope':
			segmented_image = self.get_network_output(self.image,'binary')
			self.lyse_cells(segmented_image,self.cell_type_to_lyse,self.lysis_mode)
		else:
			segmented_image = self.get_network_output(self.image,'multi')
			# segmented_image = self.get_network_output(self.hallucination_img,'multi')
			# cv2.imshow('Cell Outlines and Centers',segmented_image)
			# lyse all cells in view
			self.lyse_cells(segmented_image,self.cell_type_to_lyse,self.lysis_mode)
		if self.auto_lysis == False:
			self.stop_laser_flash_signal.emit()	
			return
		if self.lysed_cell_count >= self.cells_to_lyse: 
			self.delay()
			self.return_to_original_position(self.well_center)
			self.stop_laser_flash_signal.emit()	
			return	
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
		if len(cell_contours) > 0:
			for i in range(len(cell_contours)):			
				contour = cell_contours[i]
				point_number = contour.shape[0] 
				# this block is responsible for vectoring from one contour start to another
				if i == 0:
					contour_start = contour[0].reshape(2)
					self.move_to_target(contour_start - window_center,True)
					old_center = np.copy(contour_start)
				else:
					# return_vec =  np.sum((cell_contours[i-1].reshape(-1,2)),axis = 1) 
					new_center = contour[0].reshape(2)
					self.move_to_target(-return_vec.reshape(2) - contour_start + new_center,False)
					old_center = new_center
					contour_start = np.copy(new_center)
				# now turn on the autofire				
				time.sleep(.1)
				self.qswitch_screenshot_signal.emit(2)
				self.ai_fire_qswitch_signal.emit(True)				
				# this block is responsible for vectoring around the contour
				return_vec = np.zeros((2))
				for j in range(1,point_number):		
					new_center = contour[j].reshape(2)		
					move_vec = -old_center + new_center
					scaled_move_vec = move_vec*1.5
					return_vec = np.add(return_vec,scaled_move_vec)
					print(return_vec,return_vec.shape,scaled_move_vec.shape)
					self.qswitch_screenshot_signal.emit(1)
					self.move_to_target(scaled_move_vec,False)
					old_center = new_center
					time.sleep(.1)
				self.lysed_cell_count += 1
				self.qswitch_screenshot_signal.emit(2)
				self.ai_fire_qswitch_signal.emit(False)
				self.delay()
				if self.auto_lysis == False:
					self.stop_laser_flash_signal.emit()	
					return
				if self.lysed_cell_count >= self.cells_to_lyse: 
					self.delay()
					self.return_to_original_position(self.well_center)
					self.stop_laser_flash_signal.emit()	
					return	

	def direct_lysis(self,cell_centers):
		window_center = np.array([125./2,125./2])
		if len(cell_centers) < 2: return
		cell_centers = cell_centers[1:]

		print('centers:',cell_centers)
		old_center = cell_centers[0]
		self.move_to_target(old_center-window_center,True)
		self.delay()
		self.qswitch_screenshot_signal.emit(10)
		for i in range(3):
			self.ai_fire_qswitch_signal.emit(False)
			self.delay()
		self.lysed_cell_count += 1
		if self.lysed_cell_count >= self.cells_to_lyse: 				
				self.return_to_original_position(self.well_center)
				self.stop_laser_flash_signal.emit()	
				return			
		if len(cell_centers) > 1:
			for i in range(1,len(cell_centers)):
				self.qswitch_screenshot_signal.emit(15)
				self.move_to_target(-old_center + cell_centers[i],False)
				old_center = cell_centers[i]				
				self.delay()
				for i in range(3):	
					self.ai_fire_qswitch_signal.emit(False)
					self.delay()
				self.delay()
				self.lysed_cell_count += 1
				if self.auto_lysis == False:
					self.stop_laser_flash_signal.emit()	
					return
				if self.lysed_cell_count >= self.cells_to_lyse: 
					self.delay()
					self.return_to_original_position(self.well_center)
					self.stop_laser_flash_signal.emit()	
					return	

	def get_contours_and_centers(self,confidence_image):
		_, contours, _ = cv2.findContours(np.uint8(confidence_image), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		cell_image = np.zeros((125,125))
		cell_contours = []
		cell_centers = []
		for contour in contours:
			# print(cv2.contourArea(contour))
			if cv2.contourArea(contour) > 20:
				(x,y),radius = cv2.minEnclosingCircle(contour)
				center = (int(x),int(y))
				cell_contours.append(contour)				
				cv2.circle(cell_image,center,2 ,(255,0,0),-1)
				center = np.array(center)
				cell_centers.append(center)
		cv2.drawContours(cell_image, contours, -1, (255,255,255), 1)
		cv2.imshow('Cell Outlines and Centers',cell_image)
		return cell_contours,cell_centers				

	def threshold_based_on_type(self,segmented_image,cell_type):
		if cell_type == 'green':
			_,confidence_image = cv2.threshold(segmented_image[:,:,1],.9,1,cv2.THRESH_BINARY)
		elif cell_type == 'red':
			_,confidence_image = cv2.threshold(segmented_image[:,:,2],.9,1,cv2.THRESH_BINARY)
		elif cell_type == 'green hope':
			# assumes a binary image!
			# TODO: find the optimal location on the AUC curve for the threshold
			_,confidence_image = cv2.threshold(segmented_image,.9,1,cv2.THRESH_BINARY)
		return confidence_image

	def move_to_target(self,center,goto_reticle = False):
		# we need to scale our centers up to the proper resolution and then 
		# send it to the stage
		x = center[0]*851/125
		y = center[1]*681/125
		self.localizer_move_signal.emit(np.array([x,y]),goto_reticle,True,True)


	

