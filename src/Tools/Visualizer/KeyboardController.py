import numpy as np
from OpenGL.GL import *

import Visualizer

window = None
class KeyboardController(object):
    def __init__(self,window_):
        global window
        if not isinstance(window_, Visualizer.Visualizer):
            raise RuntimeError("Invalid vehicle provided")
        window = window_


    def processKeyboardInput(self,char, x, y):
        global window
        if not isinstance(window, Visualizer.Visualizer):
            raise RuntimeError("Invalid vehicle provided")
        speed = 0.1
        if(char=='a'):
            glTranslatef(speed,0,0)
            window.camera[0] += speed
        if(char=='d'):
            glTranslatef(-speed,0,0)
            window.camera[0] -= speed
        if(char=='w'):
            glTranslatef(0,0,speed)
            window.camera[2] += speed
        if(char=='s'):
            glTranslatef(0,0,-speed)
            window.camera[2] -= speed
        if(char=='p'):
            print "vehicle: ",window.vehicle.quad.heading,window.vehicle.getPositionVector()
            print "camera: ", window.camera
            print "drone_in_space: ", window.dronePos
