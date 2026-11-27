import sys
import time
import py_ihm.cfg as cfg
import py_ihm.init as init
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream, QTimer
from PyQt5 import QtCore, QtGui, QtWidgets

import rclpy
from rclpy.node import Node

from pyqtconsole.console import PythonConsole
import pyqtconsole.highlighter as hl

from std_msgs.msg import String, Float32, UInt32
import sensor_msgs.msg

import py_ihm.cfg as cfg
import py_ihm.command as cmd

import py_ihm.plotswidget as pltw
from py_ihm.ihm_ui import Ui_IHMProjet


def define_format():
	new_format ={
	'keyword':	hl.format('blue', 'bold'),
	'operator':   hl.format('red'),
	'brace':	  hl.format('darkGray'),
	'defclass':   hl.format('black', 'bold'),
	'string':	 hl.format('magenta'),
	'string2':	hl.format('darkMagenta'),
	'comment':	hl.format('darkGreen', 'italic'),
	'self':	   hl.format('black', 'italic'),
	'numbers':	hl.format('brown'),
	'inprompt':   hl.format('darkBlue', 'bold'),
	'outprompt':  hl.format('darkRed', 'bold'),
	}
	return new_format

def greet():
	print("hello world")


class IHMWindow(QMainWindow):
	## init ##
	def __init__(self):
		super(IHMWindow,self).__init__()

		## assign to the main window the ui made 
		self.ui = Ui_IHMProjet()
		self.ui.setupUi(self)

		self.setWindowTitle("Projet Robot - SEN - 2024P")
		self.setWindowIcon(QtGui.QIcon("icons/icon_robot.png"))

		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.ui.command_w.sizePolicy().hasHeightForWidth())

		self.ui.gridLayout.replaceWidget(self.ui.graphs_w, pltw.MainWindow())
		self.ui.graphs_w.setObjectName("graphs_w")
		self.ui.graphs_w.setSizePolicy(sizePolicy)

		### console init
		console = PythonConsole(formats =define_format())
		console.push_local_ns('greet', greet)
		console.show()
		console.eval_in_thread()
		self.ui.gridLayout.replaceWidget(self.ui.terminal_w, console)
		self.ui.terminal_w.setObjectName("terminal_w")
		self.ui.terminal_w.setSizePolicy(sizePolicy)

		###

		self.ui.icon_w.setHidden(True)
		self.ui.settings_w.setHidden(True)

		self.last_button_pressed = None

		# ROS2
		self.tinit = time.time()

		rclpy.init(args=None) 
		self.node = Node('py_ihm_node')
		self.publisher_ = self.node.create_publisher(String, 'pyqt_topic_send', 10)
		self.i = 0

		self.mode_publisher = self.node.create_publisher(String, 
			'pyqt_topic_send_mode', 10)
		
		self.motorspeed_publisher = self.node.create_publisher(Float32, 
			'pyqt_topic_send_motorspeed', 10)
		
		self.robotspeed_publisher = self.node.create_publisher(Float32,
			'pyqt_topic_send_robotspeed', 10)

		self.state_publisher = self.node.create_publisher(String,
			'pyqt_topic_send_state', 10)

		self.leftmotor_publisher = self.node.create_publisher(Float32,
			'pyqt_topic_send_leftmotor', 10)

		self.rightmotor_publisher = self.node.create_publisher(Float32,
			'pyqt_topic_send_rightmotor', 10)

		
		self.subscription = self.node.create_subscription(
			String,
			'pyqt_topic_rec',
			self.listener_callback,
			10)
		
		self.subscription  # prevent unused variable warning

		self.back_dist_sub = self.node.create_subscription(
			UInt32,
			'pyqt_topic_rx_backdist',
			self.back_dist_cb,
			10)

		self.back_dist_sub # prevent unused variable warning

		self.frontleft_dist_sub = self.node.create_subscription(
			UInt32,
			'pyqt_topic_rx_frontleftdist',
			self.frontleft_dist_cb,
			10)

		self.frontleft_dist_sub # prevent unused variable warning

		self.frontright_dist_sub = self.node.create_subscription(
			UInt32,
			'pyqt_topic_rx_frontrightdist',
			self.frontright_dist_cb,
			10)

		self.frontright_dist_sub # prevent unused variable warning

		self.motorright_speed_sub = self.node.create_subscription(
			Float32,
			'pyqt_topic_rx_rightspeed',
			self.rightspeed_cb,
			10)

		self.motorright_speed_sub

		self.motorleft_speed_sub = self.node.create_subscription(
			Float32,
			'pyqt_topic_rx_leftspeed',
			self.leftspeed_cb,
			10)

		self.motorleft_speed_sub

		self.robot_speed_sub = self.node.create_subscription(
			Float32,
			'pyqt_topic_rx_robotspeed',
			self.robotspeed_cb,
			10)

		self.robot_speed_sub



		self.camera_sub = self.node.create_subscription(
			sensor_msgs.msg.Image,
			'camera/src_frame',
			self.camera_cb,
			10)

		self.camera_sub
			  
		self.timer = QTimer()
		self.timer.timeout.connect(self.onTimerTick)   
		self.timer.start(5)	  
		#===================================
		#	command_w
		#===================================

		self.ui.up_distance_SpBox.valueChanged.connect(lambda: self.up_command_spin())
		self.ui.right_distance_SpBox.valueChanged.connect(lambda: self.right_command_spin())
		self.ui.down_distance_SpBox.valueChanged.connect(lambda: self.down_command_spin())
		self.ui.left_distance_SpBox.valueChanged.connect(lambda: self.left_command_spin())

		self.ui.vitesse_SpBox.valueChanged.connect(lambda: self.robot_speed_spin())
		self.ui.vmoteur_SpBox.valueChanged.connect(lambda: self.motor_speed_spin())
		self.ui.mode_cB.currentTextChanged.connect(lambda : self.mode_spin())

		#===================================
		#	settings_w
		#===================================

		self.ui.graph_cB.currentTextChanged.connect(lambda : self.type_graph_spin())
		self.ui.flux_cB.currentTextChanged.connect(lambda : self.default_flux_spin())
		self.ui.mode_default_cB.currentTextChanged.connect(lambda : self.mode_default_spin())

		self.ui.G1_ymin_Checkbox.stateChanged.connect(lambda: self.gr1_min_check())
		self.ui.G1_ymax_Checkbox.stateChanged.connect(lambda: self.gr1_max_check())
		self.ui.G2_ymin_Checkbox.stateChanged.connect(lambda: self.gr2_min_check())
		self.ui.G2_ymax_Checkbox.stateChanged.connect(lambda: self.gr2_max_check())


		self.ui.tmin_time_SpBox.valueChanged.connect(lambda: self.tmin_spin())
		self.ui.tmax_time_Spbox.valueChanged.connect(lambda: self.tmax_spin())
		self.ui.te_time_SpBox.valueChanged.connect(lambda: self.te_spin())
		self.ui.G1_ymin_SpBox.valueChanged.connect(lambda: self.G1_ymin_spin())
		self.ui.G1_ymax_SpBox.valueChanged.connect(lambda: self.G1_ymax_spin())
		self.ui.G2_ymin_SpBox.valueChanged.connect(lambda: self.G2_ymin_spin())
		self.ui.G2_ymax_SpBox.valueChanged.connect(lambda: self.G2_ymax_spin())

	#===================================
	#	command_w
	#===================================
	## Callback ROS2

	def onPushSend(self):
		msg = String()
		msg.data = 'Hello World: %d' % self.i
		self.publisher_.publish(msg)
		print('Publishing: "%s"' % msg.data)
		self.i += 1
		
	def listener_callback(self, msg):
		print('I heard: "%s"' % msg.data)	
		
	def onTimerTick(self):  
		rclpy.spin_once(self.node,executor=None, timeout_sec=0.01)


	def back_dist_cb(self, msg):
		print("Received : "+str(msg))
		self.ui.rear_distance_lcd.setProperty("value", float(msg))

	def frontleft_dist_cb(self, msg):
		print("Received : "+str(msg))
		self.ui.frontleft_distance_lcd.setProperty("value", float(msg))

	def frontright_dist_cb(self, msg):
		print("Received : "+str(msg))
		self.ui.frontright_distance_lcd.setProperty("value", float(msg))

	def rightspeed_cb(self, msg):
		print("Received :"+str(msg))

		##update du plot left_speed
		self.ui.terminal_w.update_speed(float(msg), 
										round(self.tinit - time.time(), 4),
										"Right")

	def leftspeed_cb(self, msg):
		print("Received :"+str(msg))

		##update du plot right_speed
		self.ui.terminal_w.update_speed(float(msg), 
										round(self.tinit - time.time(), 4),
										"Left")

	def robotspeed_cb(self, msg):
		print("Received picture :"+str(msg))

	def camera_cb(self, msg):
		print("Received picture :"+str(msg))


	def send_leftmotor(self, value):
		msg = Float32()
		msg.data = value
		self.leftmotor_publisher.publish(msg)

	def send_rightmotor(self, value):
		msg = Float32()
		msg.data = value
		self.rightmotor_publisher.publish(msg)

	def send_state(self, state):
		msg = String()
		msg.data = str(state)
		self.state_publisher.publish(msg)

	def mode_publisher(self, mode):
		msg = String()
		msg.data = str(mode)
		self.mode_publisher.publish(msg)


	### Central pad
	# Buttons
	def on_up_command_b_clicked(self):
		if (self.last_button_pressed != "up_command_b"):
			print("UP CLICKED")
			self.last_button_pressed = "up_command_b"
		else:
			self.last_button_pressed = None

	def on_left_command_b_clicked(self):
		if (self.last_button_pressed != "left_command_b"):
			print("LEFT CLICKED")
			self.last_button_pressed = "left_command_b"
		else:
			self.last_button_pressed = None

	def on_nomove_b_clicked(self):
		if (self.last_button_pressed != "nomove_b"):
			print("NOMOVE")
			self.last_button_pressed = "nomove_b"
		else:
			self.last_button_pressed = None

	def on_right_command_b_clicked(self):
		if (self.last_button_pressed != "right_command_b"):
			print("RIGHT CLICKED")
			self.last_button_pressed = "right_command_b"
		else:
			self.last_button_pressed = None

	def on_down_command_b_clicked(self):
		if (self.last_button_pressed != "down_command_b"):
			print("DOWN CLICKED")
			self.last_button_pressed = "down_command_b"
		else:
			self.last_button_pressed = None

	def on_upleft_command_b_clicked(self):
		if (self.last_button_pressed != "upleft_command_b"):
			print("upleft CLICKED")
			self.last_button_pressed = "upleft_command_b"
		else:
			self.last_button_pressed = None

	def on_upright_command_b_clicked(self):
		if (self.last_button_pressed != "upright_command_b"):
			print("upright CLICKED")
			self.last_button_pressed = "upright_command_b"
		else:
			self.last_button_pressed = None

	def on_downright_command_b_clicked(self):
		if (self.last_button_pressed != "downright_command_b"):
			print("downright CLICKED")
			self.last_button_pressed = "downright_command_b"
		else:
			self.last_button_pressed = None

	def on_downleft_command_b_clicked(self):
		if (self.last_button_pressed != "downleft_command_b"):
			print("downleft CLICKED")
			self.last_button_pressed = "downleft_command_b"
		else:
			self.last_button_pressed = None

	# QDoubleSpinBox
	def up_command_spin(self):
		value = self.ui.up_distance_SpBox.value()
		print("NEW UP VALUE :",value)
		cfg.front_speed = value

	def right_command_spin(self):
		value = self.ui.right_distance_SpBox.value()
		print("NEW RIGHT VALUE :",value)
		cfg.right_speed = value

	def down_command_spin(self):
		value = self.ui.down_distance_SpBox.value()
		print("NEW DOWN VALUE :",value)
		cfg.rear_speed = value

	def left_command_spin(self):
		value = self.ui.left_distance_SpBox.value()
		print("NEW LEFT VALUE :",value)
		cfg.left_speed = value
	
	#LCDNumber

	def update_lcd_frontright(self):
		#self.ui.frontright_distance_lcd.display(nval) ## display new value
		pass

	def update_lcd_frontleft(self):
		#self.ui.frontleft_distance_lcd.display(nval) ## display new value
		pass

	def update_lcd_rear(self):
		#self.ui.rear_distance_lcd.display(nval) ## display new value
		pass


	### Left pad

	def on_start_b_clicked(self):
		if (self.last_button_pressed != "start_b"):
			print("start CLICKED")
			self.last_button_pressed = "start_b"
		else:
			self.last_button_pressed = None

	def robot_speed_spin(self):
		value = self.ui.vitesse_SpBox.value()
		print("NEW robot VALUE :",value)

	def motor_speed_spin(self):
		value = self.ui.vmoteur_SpBox.value()
		print("NEW motor VALUE :",value) 

	def mode_spin(self):
		value = self.ui.mode_cB.currentText()
		print("NEW MODE VALUE :",value) 

	#===================================
	#	settings_w
	#===================================

	def type_graph_spin(self):
		value = self.ui.graph_cB.currentText()
		print("NEW graph type VALUE :",value) 

	def default_flux_spin(self):
		value = self.ui.flux_cB.currentText()
		print("NEW camera flux VALUE :",value) 

	def mode_default_spin(self):
		value = self.ui.mode_default_cB.currentText()
		print("NEW MODE VALUE :",value)

	def gr1_min_check(self):
		value = self.ui.G1_ymin_Checkbox.checkState()
		print("NEW gr1 check VALUE :",value)

	def gr1_max_check(self):
		value = self.ui.G1_ymax_Checkbox.checkState()
		print("NEW gr1 check VALUE :",value)  

	def gr2_min_check(self):
		value = self.ui.G2_ymin_Checkbox.checkState()
		print("NEW gr2 check VALUE :",value)  

	def gr2_max_check(self):
		value = self.ui.G2_ymax_Checkbox.checkState()
		print("NEW gr2 check VALUE :",value)

	def tmin_spin(self):
		value = self.ui.tmin_time_SpBox.value()
		print("NEW tmin VALUE :",value) 

	def tmax_spin(self):
		value = self.ui.tmax_time_Spbox.value()
		print("NEW tmax VALUE :",value) 

	def te_spin(self):
		value = self.ui.te_time_SpBox.value()
		print("NEW te VALUE :",value) 

	def G1_ymin_spin(self):
		value = self.ui.G1_ymin_SpBox.value()
		print("NEW G1 ymin VALUE :",value) 

	def G1_ymax_spin(self):
		value = self.ui.G1_ymax_SpBox.value()
		print("NEW G1 ymax VALUE :",value) 

	def G2_ymin_spin(self):
		value = self.ui.G2_ymin_SpBox.value()
		print("NEW G2 ymin VALUE :",value) 

	def G2_ymax_spin(self):
		value = self.ui.G2_ymax_SpBox.value()
		print("NEW G2 ymax VALUE :",value)	 

def main(args=None):
	app = QApplication(sys.argv)
	##init
	## loading style file
	with open("/home/e2020/t0demora/Bureau/proj_robot_2024p-main/pyqt_ihm_ros2_ws/src/py_ihm/py_ihm/ihm_style.qss", "r") as style_file:
		style_str = style_file.read()
	app.setStyleSheet(style_str)
	##main
	window = IHMWindow()
	window.show()
	##quit

	sys.exit(app.exec())


if __name__ == "__main__":
	main()
