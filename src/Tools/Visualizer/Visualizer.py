'''
Created on 3 mar 2017

@author: Mateusz Raczynski
'''
# needs http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl

from threading import Thread
import time

import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from KeyboardController import KeyboardController
from VehicleApi import QuadcopterApi


class Visualizer(object):
    def __init__(self, vehicleTracked):
        self.dronePos = np.array([0, 0, -7])
        self.camera = np.array([0, 3, 9])
        self.cameraUpdated = True
        self.vehicle = None
        cs = 1
        self.verticies = (
            (cs, -cs, -cs),
            (cs, cs, -cs),
            (-cs, cs, -cs),
            (-cs, -cs, -cs),
            (cs, -cs, cs),
            (cs, cs, cs),
            (-cs, -cs, cs),
            (-cs, cs, cs)
        )

        self.edges = (
            (0, 1),
            (0, 3),
            (0, 4),
            (2, 1),
            (2, 3),
            (2, 7),
            (6, 3),
            (6, 4),
            (6, 7),
            (5, 1),
            (5, 4),
            (5, 7)
        )
        self.kbcntrl = KeyboardController(self)
        if not isinstance(vehicleTracked, QuadcopterApi):
            raise RuntimeError("Invalid vehicle provided")
        self.vehicle = vehicleTracked
        glutInit()
        glutInitWindowSize(640, 480)
        glutCreateWindow("Visualizer")
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutDisplayFunc(self.render)
        glutIdleFunc(self.update)
        glutKeyboardFunc(self.kbcntrl.processKeyboardInput)
        self.initialize()

    def run(self):
        glutMainLoop()

    def Cube(self):
        glColor3f(0.0, 0.9, 0.0)
        glLineWidth(4.0)
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.verticies[vertex])
        glEnd()

    def drawDrone(self):
        glColor3f(0.3, 0.3, 1.0)
        glPointSize(6.0)
        glBegin(GL_POINTS)
        glVertex3fv(self.dronePos)
        glEnd()

    def initialize(self):
        print 'OpenGL Context initialized.\n Version: ',glGetString(GL_VERSION)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        display = (800, 600)

        fieldOfView = 60.0
        aspect = display[0] / display[1]
        zNear = 0.1
        zFar = 50

        glClearColor(0.3, 0.3, 0.3, 0.0)

        glColor3f(0.0, 0.0, 0.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fieldOfView, (aspect), zNear, zFar)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(self.camera[0], self.camera[1], self.camera[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    def setDronePos(self, position):
        self.dronePos = position
        # self.dronePos[0] = position[0]
        # self.dronePos[1] = position[1]
        # self.dronePos[2] = position[2]
        '''dcamera = [0,0,0]
        dcamera[0] = position[0] - camera[0]
        dcamera[1] = position[1] - camera[1]
        dcamera[2] = position[2] - camera[2]
        glTranslatef(dcamera[0],dcamera[1],dcamera[2])'''

        # glMatrixMode(GL_MODELVIEW)
        # glLoadIdentity()
        # gluLookAt(camera[0], camera[1], camera[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    def moveCamera(deltaPosition):

        return

    def render(self):
        if self.cameraUpdated:
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            gluLookAt(self.camera[0], self.camera[1], self.camera[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
            self.cameraUpdated = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.Cube()
        self.drawDrone()
        glFlush()

    lastTime = -1
    deltaTime = 0
    updTime = 0

    def update(self):
        self.deltaTime = -1
        now = int(round(time.time() * 1000))
        if (self.lastTime == -1):
            self.deltaTime = 0
        else:
            self.deltaTime = now - self.lastTime
        self.lastTime = now
        self.updTime = self.updTime + self.deltaTime
        if (self.updTime > 60):
            self.updateVehiclePosition()
            self.updTime = 0
            glutPostRedisplay()
        return

    def updateVehiclePosition(self):
        if (self.vehicle is not None):
            position = self.vehicle.getPositionVector()
            if not position is None:
                self.setDronePos(tENUtoXYZ(position))
        else:
            self.setDronePos(np.array([2.0, 2.0, 2.0]))


def tENUtoXYZ(vector):
    """
    :param vector:  vector to transform
    :return:        transformed vector
    This function transform [east,north,up] to OpenGL coordinates [x,y,z]
    """
    nVec = [0, 0, 0]
    nVec[0] = vector[0]
    nVec[1] = vector[2]
    nVec[2] = -vector[1]
    return nVec


def createWindow(vehicle, continueFunction=None, *fargs):
    """
    :param vehicle:             object to track
    :param continueFunction:    function to be called after window creation
    :param fargs:               arguments of continueFunction
    This function has to be executed from main thread and it doesn't return!
    Use continueFunction argument to execute other part of program
    or create other thread on your own before executing this.
    """
    if not continueFunction is None:
        if len(fargs) == 0:
            args = ()
        else:
            args = fargs[0], fargs[1:]
        thread = Thread(name='visualizeCallbackThread', args=args)
        thread.run = continueFunction
        thread.start()

    vis = Visualizer(vehicle)
    vis.run()


if __name__ == '__main__':
    createWindow(None)
