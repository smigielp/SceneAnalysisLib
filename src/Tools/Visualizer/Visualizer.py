'''
Created on 3 mar 2017

@author: Mateusz Raczynski
'''
# needs http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl
# todo: change projection matrix on window resize
import threading
from threading import Thread, RLock, Condition
import time

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays._arrayconstants import GL_UNSIGNED_BYTE

import KeyboardController
from VehicleApi import QuadcopterApi
import Shader

from ctypes import c_float

from ModelObject import ModelObject

from Transformations import *
from Parser import loadObjectFromObjFile

OpenGL.FULL_LOGGING = True
_float = c_float
float32 = np.float32

OGLThreadContextName = '__main__'

class Visualizer(object):
    def __init__(self, vehicleTracked, shouldInitialize=False):

        self.dronePos = np.array([0, 0, -7])

        self.cameraUpdated = True
        self.cameraC = Visualizer.Camera()
        cs = 1.0
        self.verticies = np.array((
            (cs, -cs, -cs),
            (cs, cs, -cs),
            (-cs, cs, -cs),
            (-cs, -cs, -cs),
            (cs, -cs, cs),
            (cs, cs, cs),
            (-cs, -cs, cs),
            (-cs, cs, cs)
        ), dtype=float32)

        self.edges = np.array((
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
        ), dtype=np.uint32)

        self.kbcntrl = KeyboardController.KeyboardController(self)

        self.vehicle = None
        if not isinstance(vehicleTracked, QuadcopterApi) and vehicleTracked is not None:
            raise RuntimeError("Invalid vehicle provided")
        self.vehicle = vehicleTracked

        self._regModels = list()
        self._modelsLock = RLock()

        self._frame = None
        self._waitingOnFrame = False
        self._frameAvailability = Condition()
        self._waitingAmount = 0
        self._useCameraFromVehicle = False

        self.shader = None
        self.uniforms = None
        self.buftest = None
        self.obj = None

        if shouldInitialize:
            self.initialize()

    def getWindowSize(self):
        return self.cameraC.width,self.cameraC.height

    def obtainModelObject(self, drawType='STATIC', modelType='POINTS'):
        """
        :param drawType:    static/dynamic/stream
        :param modelType:   type of model
        :return:            registered object
        For more info check ModelObject.py
        """
        model = ModelObject(drawType, modelType)
        self.registerModelObject(model)
        return model

    def registerModelObject(self, model):
        """
        :param model:  object to be registered
        For more info check ModelObject.py
        """
        if not isinstance(model, ModelObject):
            raise RuntimeError("Invalid model provided.")
        with self._modelsLock:
            self._regModels.append(model)

    def run(self):
        glutMainLoop()

    def windowResized(self, nWidth, nHeight):
        self.cameraC.aspect = float(nWidth) / nHeight
        self.cameraC.width = nWidth
        self.cameraC.height = nHeight
        glViewport(0, 0, nWidth, nHeight)
        self.cameraC.projectionUpdate()

    def initialize(self):

        glutInit()
        glutInitWindowSize(640, 480)
        glutCreateWindow("Visualizer")
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
        glutDisplayFunc(self.render)
        glutIdleFunc(self.update)
        glutKeyboardFunc(self.kbcntrl.processKeyboardInput)
        glutReshapeFunc(self.windowResized)
        print 'OpenGL Context initialized.\n Version: ', glGetString(GL_VERSION)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glClearColor(0.3, 0.3, 0.3, 0.0)

        self.shader = Shader.loadShader()
        self.uniforms = Shader.createUniformLocations(self.shader)

        self.buftest = ModelObject(drawType='STATIC', modelType='LINES')
        self.buftest.data = self.verticies
        self.buftest.elements = self.edges.flatten()
        self.buftest.render = False
        self.buftest.color = np.array([0.2, 0.3, 0.7])
        self.registerModelObject(self.buftest)

        self.obj = self.obtainModelObject()
        self.obj.data = np.array([[0.0, 0.0, 0.0]])
        self.obj.render = True

        objects = loadObjectFromObjFile("test_Scene_1.obj",splitObjects=True)
        for object in objects:
            object.verify()
            renObject = ModelObject(obj=object,modelType="TRIANGLES")
            self.registerModelObject(renObject)
            renObject.render = True
            if object.name == "Ground":
                renObject.color = np.array([0.2, 0.5, 0.25])
            elif object.name == "RedBuilding":
                renObject.color = np.array([1.0, 0.00, 0.00])
            elif object.name == "BlueBuilding":
                renObject.color = np.array([0.0, 0.00, 1.00])
            elif object.name == "PurpleBuilding":
                renObject.color = np.array([0.64, 0.28, 0.64])
            elif object.name == "YellowBuilding":
                renObject.color = np.array([1.0, 0.94, 0.00])
            else:
                renObject.color = np.array([0.7, 0.04, 0.05])
            #if not ( object.name == "Plane001" or object.name == "Box004"):
            #    renObject.render = False
        #self.testobj = ModelObject(obj=objects[0],modelType="TRIANGLES")
        #self.testobj.color = np.array([0.2, 0.5, 0.25])
        #self.testobj.render = True
        #self.registerModelObject(self.testobj)

        glDisable(GL_CULL_FACE)
        print get_debug_output()

    def glUpdateCamera(self):
        pass
        # self._V.fill(0)
        # np.fill_diagonal(self._V, 1)
        # glCamera = -tENUtoXYZ(self.camera)
        # self._V = translate(self._V, glCamera[0], glCamera[1], glCamera[2])

    def grabFrame(self):
        """
        :return: array of pixels of current frame
        Returned image is starting from lower left corner and each pixel is in RGBA, byte format
        """

        if threading.current_thread().name == OGLThreadContextName:
            return self.grabFrameS()

        with self._frameAvailability:
            if self._waitingAmount == 0:
                self._waitingOnFrame = True
            self._waitingAmount += 1

            self._frameAvailability.wait()
            frame = self._frame

            self._waitingAmount -= 1
            if self._waitingAmount == 0:
                self._frame = None
            return frame
        pass

    def grabFrameS(self):
        """
        :return: array of pixels of current frame
        Returned image is starting from lower left corner and each pixel is in RGBA, byte format
        This function is safe only in thread with OpenGL context
        """
        frame = glReadPixels(0, 0, self.cameraC.width, self.cameraC.height, format=GL_RGBA,type=GL_UNSIGNED_BYTE, outputType=GL_UNSIGNED_BYTE)
        return frame

    def _writeFrame(self):
        if self._waitingOnFrame:
            with self._frameAvailability:
                self._frame = glReadPixels(0, 0, self.cameraC.width, self.cameraC.height, format=GL_RGBA,type=GL_UNSIGNED_BYTE, outputType=GL_UNSIGNED_BYTE)
                self._waitingOnFrame = False
                self._frameAvailability.notify_all()
        pass

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.shader)
        self.cameraC.update()
        glUniformMatrix4fv(self.uniforms[0], 1, GL_FALSE, self.cameraC.P)
        glUniformMatrix4fv(self.uniforms[1], 1, GL_TRUE, self.cameraC.V)
        #  todo: add ambient light and normal light

        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        glPointSize(8.0)
        with self._modelsLock:
            for model in self._regModels:
                model.gl_buffer()
                if model.gl_bind():
                    glUniformMatrix4fv(self.uniforms[2], 1, GL_TRUE, model.modelMatrix)
                    glUniform3f(self.uniforms[3], model.color[0], model.color[1], model.color[2])
                    glEnableVertexAttribArray(0)
                    glVertexAttribPointer(
                        0,
                        3,
                        GL_FLOAT,
                        GL_FALSE,
                        sizeof(_float) * 3,
                        None
                    )
                    if model.gl_shouldUseElem():
                        glDrawElements(model.modelType, model.bufferSize,GL_UNSIGNED_INT,None)
                    else:
                        glDrawArrays(model.modelType, 0, model.bufferSize)
                    glDisableVertexAttribArray(0)

        mess = get_debug_output()
        if len(mess) > 0:
            print mess

        if self._waitingOnFrame:
            self._writeFrame()
        glutSwapBuffers()

    lastTime = -1
    deltaTime = 0
    updTime = 0

    def update(self):
        self.deltaTime = -1
        now = int(round(time.time() * 1000))
        if self.lastTime == -1:
            self.deltaTime = 0
        else:
            self.deltaTime = now - self.lastTime
        self.lastTime = now
        self.updTime = self.updTime + self.deltaTime
        if self.updTime > 60:
            self.updateVehiclePosition()
            self.updTime = 0
            # if self.cameraUpdated:
            #    self.glUpdateCamera()
            glutPostRedisplay()
        return

    def updateVehiclePosition(self):
        if self.vehicle is not None:
            position = self.vehicle.getPositionVector()
            direction = self.vehicle.getDirectionVector()
            if position is not None:
                if not self.obj.render and not self._useCameraFromVehicle:
                    self.obj.render = True

                self.dronePos = position
                # self.obj.data = np.array([tENUtoXYZ(position)])
                self.obj.setPos(tENUtoXYZ(self.dronePos))

                if self._useCameraFromVehicle:
                    self.cameraC.position = tENUtoXYZ(self.dronePos)
                    self.obj.render = False
                    direction = tENUtoXYZ(direction)
                    direction = directionToAngles(direction)
                    self.cameraC.lookAtEulerExt(y=direction[1])

        else:
            self.obj.render = False
            # self.setDronePos(np.array([2.0, 2.0, 2.0]))

    class Camera(object):
        #todo: check if camera is really rotated by 180 deg
        def __init__(self):
            self._defaultAngle = np.array([0., math.radians(180.), 0.]) # in openGL Z axis is "behind" the screen
            self._position = np.array([0., 0., 0.])
            self._angle = self._defaultAngle+np.array([0., 0., 0.])
            self._doUpdate = True
            self._V = np.identity(4, float32)
            self.isPosENU = False
            self.__lock = RLock()

            self.width = 640
            self.height = 480

            self.P = np.identity(4, float32)
            self.fieldOfView = 80.0
            self.aspect = float(self.width) / self.height
            self.zNear = 0.1
            self.zFar = 50
            self.projectionUpdate()

        @property
        def V(self):
            return self._V

        @property
        def position(self):
            return self._position

        @position.setter
        def position(self, value):
            with self.__lock:
                self._position = value
                self._doUpdate = True

        @property
        def angle(self):
            return self._angle

        @angle.setter
        def angle(self, value):
            with self.__lock:
                self._angle = value
                self._doUpdate = True

        def move(self, x=None, y=None, z=None, xyz=None):
            """
            :param x:   amount to move towards x
            :param y:   amount to move towards y
            :param z:   amount to move towards z
            :param xyz:  vector containing all above
            """
            with self.__lock:
                if xyz is None:
                    xyz = np.array([0.0, 0.0, 0.0])
                if x is not None:
                    xyz[0] = x
                if y is not None:
                    xyz[1] = y
                if z is not None:
                    xyz[2] = z
                if self.isPosENU:
                    xyz = tXYZtoENU(xyz)
                self.position = self.position + xyz

        def moveENU(self, e=None, n=None, u=None, enu=None):
            """
            :param e:   amount to move to east
            :param n:   amount to move to north
            :param u:   amount to move to up
            :param enu:  vector containing all above
            """
            with self.__lock:
                if enu is None:
                    enu = np.array([0.0, 0.0, 0.0])
                if e is not None:
                    enu[0] = e
                if n is not None:
                    enu[1] = n
                if u is not None:
                    enu[2] = u
                if self.isPosENU:
                    self.position = self.position + enu
                else:
                    self.position = self.position + tENUtoXYZ(enu)

        def moveFRU(self, f=None, r=None, u=None, fru=None):
            """
            :param f:   amount to move to front
            :param r:   amount to move to right
            :param u:   amount to move to up
            :param fru:  vector containing all above
            """
            if fru is None:
                fru = np.array([0.0, 0.0, 0.0])
            if f is not None:
                fru[0] = f
            if r is not None:
                fru[1] = r
            if u is not None:
                fru[2] = u

            with self.__lock:
                angleYZ = self.angle[0]
                angleXZ = self.angle[1]
                fruw = np.array([fru[1], fru[2], -fru[0], 1.0])
                x, y, z, w = rotate(fruw, 0, angleXZ, 0, inv=False)

                self.move(x, y, z)

        def rotate(self, x=None, y=None, z=None, xyz=None):
            """
            :param x:   amount to rotate around x axis
            :param y:   amount to rotate around y axis
            :param z:   amount to rotate around z axis
            :param xyz:  vector containing all above
            """
            with self.__lock:
                if xyz is None:
                    xyz = np.array([0.0, 0.0, 0.0])
                if x is not None:
                    xyz[0] = x
                if y is not None:
                    xyz[1] = y
                if z is not None:
                    xyz[2] = z
                self.angle = self.angle + xyz

        def update(self):
            with self.__lock:
                if self._doUpdate:
                    angle = -self.angle  # [self.angle[0], self.angle[1]]
                    pos = -self.position
                    if self.isPosENU:
                        pos = tENUtoXYZ(pos)
                    self._V = lookAtMatrix(xyzFrom=pos, eulerAngles=angle)
                    self._doUpdate = False

        def projectionUpdate(self):
            self.P = projectionMatrix(self.fieldOfView, self.aspect, self.zNear, self.zFar)

        def lookAtEulerExt(self,eulerAngles=None,x=None,y=None,z=None):
            """
            :param eulerAngles:  vector containing all
            :param x:   amount to rotate around x axis
            :param y:   amount to rotate around y axis
            :param z:   amount to rotate around z axis
            This function sets looking direction to above values.
            If any of values x,y,z and eulerAngles are omitted, others get default value from current angle.
            Ex:
                #let's say camera has angle = [45,50,55]
                #calling:
                lookAtEulerExt(y=88)
                #would result in camera angle of [45,88,55]
            """
            with self.__lock:
                if eulerAngles is not None:
                    return self.lookAt(eulerAngles=eulerAngles)
                else:
                    xyz = self._angle
                    if x is not None:
                        xyz[0] = x
                    if y is not None:
                        xyz[1] = y
                    if z is not None:
                        xyz[2] = z
                    return self.lookAt(eulerAngles=xyz)

        def lookAt(self, xyzFrom=None, xyzAtPosition=None, xyzAtDirection=None, eulerAngles=None):
            with self.__lock:
                if xyzFrom is None:
                    xyzFrom = self.position
                else:
                    self.position = xyzFrom
                if xyzAtDirection is not None:
                    xangle, yangle, zangle = directionToAngles(xyzAtDirection)
                elif xyzAtPosition is not None:
                    xyzAtDirection = xyzAtPosition - xyzFrom
                    xangle, yangle, zangle = directionToAngles(xyzAtDirection)
                elif eulerAngles is not None:
                    xangle, yangle, zangle = eulerAngles
                else:
                    raise RuntimeError("Invalid arguments.")
                self.angle = self._defaultAngle+np.array([xangle, yangle, zangle])

        def __str__(self):
            enu = tXYZtoENU(self.position)
            t = """(Camera)
            position: %.1f , %.1f , %.1f
            position ENU: %.1f , %.1f , %.1f
            angle: %.1f , %.1f , %.1f""" \
                % (round(self.position[0], 1), round(self.position[1], 1), round(self.position[2], 1),
                   round(enu[0], 1), round(enu[1], 1), round(enu[2], 1),
                   round(math.degrees(self.angle[0]), 1), round(math.degrees(self.angle[1]), 1), round(math.degrees(self.angle[2]), 1))
            return t
    def cameraFromVehicle(self,bool):
        self._useCameraFromVehicle = bool
    def isCameraFromVehicle(self):
        return self._useCameraFromVehicle


def tENUtoXYZ(vector):
    """
    :param vector:  vector to transform
    :return:        transformed vector
    This function transform [east,north,up] to OpenGL coordinates [x,y,z]
    """
    nVec = np.array([0, 0, 0], dtype=float32)
    nVec[0] = vector[0]
    nVec[1] = vector[2]
    nVec[2] = -vector[1]
    return nVec


def tXYZtoENU(vector):
    """
    :param vector:  vector to transform
    :return:        transformed vector
    This function transform OpenGL coordinates [x,y,z] to [east,north,up]
    """
    nVec = np.array([0, 0, 0], dtype=float32)
    nVec[0] = vector[0]
    nVec[1] = vector[2]
    nVec[2] = -vector[1]
    return nVec


def get_constant(value, namespace):
    """Get symbolic constant.

    value - the (integer) token value to look for
    namespace - the module object to search in

    """

    for var in dir(namespace):
        attr = getattr(namespace, var)
        if isinstance(attr, constant.Constant) and attr == value:
            return var
    return value


def get_debug_output():
    """Get the contents of the OpenGL debug log as a string."""

    from OpenGL import GL
    from OpenGL.GL.ARB import debug_output

    # details for the available log messages
    msgmaxlen = GL.glGetInteger(debug_output.GL_MAX_DEBUG_MESSAGE_LENGTH_ARB)
    msgcount = GL.glGetInteger(debug_output.GL_DEBUG_LOGGED_MESSAGES_ARB)

    # ctypes arrays to receive the log data
    msgsources = (ctypes.c_uint32 * msgcount)()
    msgtypes = (ctypes.c_uint32 * msgcount)()
    msgids = (ctypes.c_uint32 * msgcount)()
    msgseverities = (ctypes.c_uint32 * msgcount)()
    msglengths = (ctypes.c_uint32 * msgcount)()
    msglog = (ctypes.c_char * (msgmaxlen * msgcount))()

    glGetDebugMessageLog(msgcount, msgmaxlen, msgsources, msgtypes, msgids,
                         msgseverities, msglengths, msglog)

    offset = 0
    logdata = zip(msgsources, msgtypes, msgids, msgseverities, msglengths)
    for msgsource, msgtype, msgid, msgseverity, msglen in logdata:
        msgtext = msglog.raw[offset:offset + msglen].decode("ASCII")
        offset += msglen
        msgsource = get_constant(msgsource, debug_output)
        msgtype = get_constant(msgtype, debug_output)
        msgseverity = get_constant(msgseverity, debug_output)
        return ("SOURCE: {0}\nTYPE: {1}\nID: {2}\nSEVERITY: {3}\n"
                "MESSAGE: {4}".format(msgsource, msgtype, msgid,
                                      msgseverity, msgtext))
    return ""



def createWindow(vehicle):
    """
    :param vehicle: vehicle which will be tracked
    :return:        window
    This function creates thread and window with OpenGL context.
    """
    global OGLThreadContextName
    vis = Visualizer(vehicle)
    OGLThreadContextName = 'VisualizerThread'
    thread = Thread(name=OGLThreadContextName, args=(vis,), target=_createWindow)
    thread.start()
    return vis


def _createWindow(vis):
    vis.initialize()
    vis.run()



if __name__ == '__main__':
    KeyboardController.assertion = False
    createWindow(None)
