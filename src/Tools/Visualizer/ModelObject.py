'''
Created on 5 mar 2017

@author: Mateusz Raczynski
'''
from OpenGL.GL.VERSION.GL_1_5 import glGenBuffers
from OpenGL.GL.VERSION.GL_1_5 import glBindBuffer
from OpenGL.GL.VERSION.GL_1_5 import glBufferData
from OpenGL.GL.VERSION.GL_1_5 import glDeleteBuffers

from OpenGL.GL.VERSION.GL_1_5 import GL_ARRAY_BUFFER
from OpenGL.GL.VERSION.GL_1_5 import GL_ELEMENT_ARRAY_BUFFER

from OpenGL.GL.VERSION.GL_1_5 import GL_STATIC_DRAW
from OpenGL.GL.VERSION.GL_1_5 import GL_DYNAMIC_DRAW
from OpenGL.GL.VERSION.GL_1_5 import GL_STREAM_DRAW

from OpenGL.GL.VERSION.GL_1_1 import GL_POINTS
from OpenGL.GL.VERSION.GL_1_1 import GL_LINES
from OpenGL.GL.VERSION.GL_1_1 import GL_TRIANGLES
from OpenGL.GL.VERSION.GL_1_1 import GL_LINE_STRIP
from OpenGL.GL.VERSION.GL_1_1 import GL_TRIANGLE_STRIP

from Transformations import translate
from Transformations import scale
from Transformations import rotateDegrees

from OpenGL.arrays import vbo

# from OpenGL.GL import VBO
# from ctypes import sizeof
from threading import RLock
import numpy as np

from Parser import Object3d
from Parser import loadObjectFromObjFile

DRAWTYPES = dict([('STATIC', GL_STATIC_DRAW), ('DYNAMIC', GL_DYNAMIC_DRAW), ('STREAM', GL_STREAM_DRAW)])
MODELTYPES = dict([('LINES', GL_LINES), ('POINTS', GL_POINTS), ('TRIANGLES', GL_TRIANGLES),
                   ('LINE_STRIP', GL_LINE_STRIP), ('TRIANGLE_STRIP', GL_TRIANGLE_STRIP)])


class ModelObject(object):
    def __init__(self, drawType='STATIC', modelType='POINTS',obj=None):
        """
        :param drawType:  acceptable values: 'STATIC', 'DYNAMIC' or 'STREAM'
        :param modelType: acceptable values: 'LINES', 'POINTS' or 'TRIANGLES'
        drawType specifies how often is this object used (rendered) and modified.
        STATIC - modified once and used very frequently
        DYNAMIC - modified and used frequently
        STREAM - modified after every few (or one) use

        Example usage:
            myModel = ModelObject(modelType='LINES')
            myModel.data = House.vertices
            myModel.color = np.array([1.,1.,1.])
            window.registerModelObject(myModel)
            #do other stuff#
            #you can modify your object later
            myModel.move([0,-2.,0])
            myModel.data = Car.vertices
        """
        self._bufferId = long(-1)
        self._bufferSize = -1
        self._bufferIdElements = long(-1)
        self._bufferSizeElements = -1
        self._updateBuffer = False
        self._data = None
        self._elements = None
        self._render = False
        self._lock = RLock()
        if drawType not in DRAWTYPES:
            raise RuntimeError("Invalid drawing type.")
        self._type = DRAWTYPES[drawType]
        if modelType not in MODELTYPES:
            raise RuntimeError("Invalid model type.")
        self._mtype = MODELTYPES[modelType]

        self._updateObjectMatrix = False
        self._objectMatrix = np.identity(4)
        self._rotation = np.array([0.0, 0.0, 0.0])
        self._position = np.array([0.0, 0.0, 0.0])
        self._scale = np.array([1.0, 1.0, 1.0])
        self._color = np.array([1.0, 0.0, 0.0])

        #todo: make sure elements and vertexArray is not None
        if obj is not None:
            self.elements = obj.elements
            self.data = obj.vertexArray

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        with self._lock:
            self._color = value

    def updateObjectMatrix(self):
        with self._lock:
            self._updateObjectMatrix = False
            self._objectMatrix = np.identity(4)
            self._objectMatrix = rotateDegrees(self._objectMatrix, xyz=self._rotation)
            self._objectMatrix = scale(self._objectMatrix, xyz=self._scale)
            self._objectMatrix = translate(self._objectMatrix, xyz=self._position)

    @property
    def modelMatrix(self):
        with self._lock:
            if self._updateObjectMatrix:
                self.updateObjectMatrix()
            return self._objectMatrix

    @modelMatrix.setter
    def modelMatrix(self, value):
        raise RuntimeError("Model matrix can't ne manually overridden ")

    def setPos(self, vector):
        with self._lock:
            self._position = vector
            self._updateObjectMatrix = True
            return

    def move(self, vector):
        with self._lock:
            self._position = self._position + vector
            self._updateObjectMatrix = True
            return

    def rotate(self, rotVector):
        with self._lock:
            self._rotation += rotVector
            self._updateObjectMatrix = True
            return

    def scale(self, vector):
        with self._lock:
            self._scale += vector
            self._updateObjectMatrix = True
            return

    @property
    def bufferId(self):
        """Get OpenGL buffer id"""
        return self._bufferId

    @property
    def bufferSize(self):
        if self._bufferIdElements>0:
            return self._bufferSizeElements
        return self._bufferSize

    @property
    def modelType(self):
        return self._mtype

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        # todo: convert to np.array if needed
        with self._lock:
            self._data = data
            self._updateBuffer = True
            if data is None:
                self._bufferSize = -1
            else:
                self._bufferSize = len(self._data)

    def setData(self, data, isVerticesArray=True):
        """
        :param data:             numpy.array
        :param isVerticesArray:  array format, specifies if array contains grouped coordinates which create vertices
        """
        # todo: convert to np.array if needed
        with self._lock:
            self.data = data
            if data is None:
                return
            if not isVerticesArray:
                self._bufferSize = int(len(self._data) / 3)

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, elements):
        # todo: convert to np.array if needed
        with self._lock:
            self._elements = elements
            self._updateBuffer = True
            if elements is None:
                self._bufferSizeElements = -1
            else:
                self._bufferSizeElements = len(self._elements)

    def setElements(self, elements):
        """
        :param elements:             numpy.array
        :param isVerticesArray:  array format, specifies if array contains grouped coordinates which create vertices
        """
        # todo: convert to np.array if needed
        with self._lock:
            self.elements = elements

    def clone(self,fullClone = False):
        """
        :param fullClone: whether pos,rot etc should be cloned or not
        :return: ModelObject
        Returns ModelObject which has same buffer as this model
        That new model has to be registered before being able to render.
        Changes of data in buffers (like vertices,normals,elements) will affect also the other model but
        position,rotation etc are separate and can be freely modified
        """
        # todo: complete clone func
        pass

    @property
    def render(self):
        return self._render

    @render.setter
    def render(self, value):
        with self._lock:
            self._render = value

    def gl_buffer(self):
        with self._lock:
            if self._updateBuffer:
                if self._data is None :
                    if self._bufferId == -1:
                        raise RuntimeError("Data was set to None")
                    else:
                        glDeleteBuffers(self._bufferId)
                        self._bufferId = long(-1)
                else:
                    if self._bufferId == -1:
                        self._bufferId = long(glGenBuffers(1))
                    glBindBuffer(GL_ARRAY_BUFFER, self._bufferId)
                    glBufferData(GL_ARRAY_BUFFER, self._data, self._type)


            if self._updateBuffer:
                if self._elements is not None:
                    if self._bufferIdElements == -1:
                        self._bufferIdElements = long(glGenBuffers(1))
                    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._bufferIdElements)
                    glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.elements, GL_STATIC_DRAW)
                elif self._bufferIdElements > 0:
                    glDeleteBuffers(self._bufferIdElements)
                    self._bufferIdElements = long(-1)



            self._updateBuffer = False

    def gl_release(self):
        if self._bufferId > 0:
            glDeleteBuffers(1, self._bufferId)
            self._bufferId = long(-1)
        if self._bufferIdElements > 0:
            glDeleteBuffers(1, self._bufferIdElements)
            self._bufferIdElements = long(-1)

    def gl_bind(self):
        # todo: add normals
        with self._lock:
            if not self._render or self._data is None or self._bufferId == -1:
                return False
            elif self._bufferId == -2:
                raise RuntimeError("Buffer was already released.")
            try:
                glBindBuffer(GL_ARRAY_BUFFER, self._bufferId)
                if self._bufferIdElements > 0:
                    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self._bufferIdElements)
            except Exception as e:
                self._render = False
                print e
                return False
            return True

    def gl_shouldUseElem(self):
        if self._bufferIdElements > 0:
            return True
        else:
            return False
