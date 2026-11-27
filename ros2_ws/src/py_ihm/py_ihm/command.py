# Command.py

## Non-Abstracted Layer, real center of the action
import py_ihm.cfg as cfg
# motor_left
# motor_right

VMAX = 3000

def lmotor(fcom, re_com, ri_com, lcom, vmax):
	res = (2/3)*fcom + (1/3)*ri_com - (2/3)*re_com - (1/3)*lcom
	res *= vmax
	return res

def rmotor(fcom, re_com, ri_com, lcom, vmax):
	res = (2/3)*fcom - (1/3)*ri_com - (2/3)*re_com + (1/3)*lcom
	res *= vmax
	return res


def front(vmax):
	res = [lmotor(1, 0, 0, 0, vmax), 
			rmotor(1, 0, 0, 0, vmax)]
	return res

def rear(vmax):
	res = [lmotor(0, 1, 0, 0, vmax), 
			rmotor(0, 1, 0, 0, vmax)]
	return res

def right(vmax):
	res = [lmotor(0, 0, 1, 0, vmax), 
			rmotor(0, 0, 1, 0, vmax)]
	return res

def left(vmax):
	res = [lmotor(0, 0, 0, 1, vmax), 
			rmotor(0, 0, 0, 1, vmax)]
	return res

def frontright(vmax):
	res = [lmotor(1, 0, 1, 0, vmax), 
			rmotor(1, 0, 1, 0, vmax)]
	return res

def frontleft(vmax):
	res = [lmotor(1, 0, 0, 1, vmax), 
			rmotor(1, 0, 0, 1, vmax)]
	return res

def rearright(vmax):
	res = [lmotor(0, 1, 1, 0, vmax), 
			rmotor(0, 1, 1, 0, vmax)]
	return res

def rearleft(vmax):
	res = [lmotor(0, 1, 0, 1, vmax), 
			rmotor(0, 1, 0, 1, vmax)]
	return res