'''
Created on 10 mar 2017

@author: Mateusz Raczynski
'''
import numpy as np
import math

float32 = np.float32


def translate(matrix, x=0,y=0,z=0,xyz=None):
    if xyz is not None:
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]
    transformationMatrix = np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1]
    ],dtype=float32)
    return transformationMatrix.dot(matrix)#matrix.dot(transformationMatrix) #transformationMatrix.dot(matrix)


def scale(matrix,x=0,y=0,z=0,xyz=None):
    if xyz is not None:
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]
    transformationMatrix = np.array([
        [x, 0, 0, 0],
        [0, y, 0, 0],
        [0, 0, z, 0],
        [0, 0, 0, 1]
    ],dtype=float32)
    return matrix.dot(transformationMatrix)


def rotate(matrix,x=0.,y=0.,z=0.,xyz=None,inv=False):
    '''

    :param matrix:
    :param x:       rotation in x axis (YZ plane)
    :param y:       rotation in y axis (XZ plane)
    :param z:       rotation in z axis (XY plane)
    :param xyz:
    :return:
    '''
    # x->z->y
    if xyz is not None:
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]
    sin = math.sin
    cos = math.cos
    xrotationMatrix = np.array([
        [1,0     , 0      ,0],
        [0,cos(x), -sin(x),0],
        [0,sin(x), cos(x) ,0],
        [0,0     , 0      ,1]
    ],dtype=float32)
    yrotationMatrix = np.array([
        [cos(y) , 0,sin(y), 0],
        [0      , 1,0     , 0],
        [-sin(y), 0,cos(y), 0],
        [0      , 0,0     , 1]
    ],dtype=float32)
    zrotationMatrix = np.array([
        [cos(z), -sin(z), 0, 0],
        [sin(z), cos(z) , 0, 0],
        [0     , 0      , 1, 0],
        [0     , 0      , 0, 1]
    ],dtype=float32)
    transformationMatrix = xrotationMatrix.dot(zrotationMatrix).dot(yrotationMatrix)
    if inv:
        return matrix.dot(transformationMatrix)
    return transformationMatrix.dot(matrix)  #matrix.dot(transformationMatrix)


def rotateDegrees(matrix,x=0,y=0,z=0,xyz=None):
    if xyz is not None:
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]
    conv = math.pi/180
    x = x*conv
    y = y*conv
    z = z*conv
    return rotate(matrix,x,y,z)


def projectionMatrix(fov, aspect,
                     zNear, zFar):
    PI_OVER_360 = math.pi / 360
    h = 1.0 / math.tan(fov * PI_OVER_360)
    neg_depth = zNear - zFar

    m = np.identity(4, dtype=float32)

    m[0][0] = h / aspect
    m[0][1] = 0
    m[0][2] = 0
    m[0][3] = 0

    m[1][0] = 0
    m[1][1] = h
    m[1][2] = 0
    m[1][3] = 0

    m[2][0] = 0
    m[2][1] = 0
    m[2][2] = (zFar + zNear) / neg_depth
    m[2][3] = -1

    m[3][0] = 0
    m[3][1] = 0
    m[3][2] = 2.0 * (zNear * zFar) / neg_depth
    m[3][3] = 0
    return m


def lookAtAngles(xyzFrom = None, xyzAtPosition = None, xyzAtDirection = None):
    if xyzFrom is None:
        raise RuntimeError("Invalid arguments.")
    if xyzAtDirection is not None:
        pass
    elif xyzAtPosition is None:
        raise RuntimeError("Invalid arguments.")
    else:
        xyzAtDirection = xyzAtPosition - xyzFrom

    return directionToAngles(xyzAtDirection)


def lookAtMatrix(xyzFrom = None, xyzAtPosition = None, xyzAtDirection = None, eulerAngles = None):
    if xyzFrom is None:
        raise RuntimeError("Invalid arguments.")
    if xyzAtDirection is not None:
        xangle,yangle,zangle = directionToAngles(xyzAtDirection)
        #pass  # xyzAtPosition = xyzFrom + xyzAtDirection
    elif xyzAtPosition is not None:
        xyzAtDirection = xyzAtPosition - xyzFrom
        xangle,yangle,zangle = directionToAngles(xyzAtDirection)
    elif eulerAngles is not None:
        xangle,yangle,zangle = eulerAngles
    else:
        raise RuntimeError("Invalid arguments.")

    viewMatrix = np.identity(4,dtype=float32)
    viewMatrix = translate(viewMatrix,xyz=xyzFrom)
    viewMatrix = rotate(viewMatrix,xangle,yangle,zangle)
    return viewMatrix


def directionToAngles(direction):
    """
    :param direction:   vector representing direction
    :return:            triple (angles on planes YZ,XZ,0) or (angles in axis X,Y,0)
    """
    YZAngle = math.atan2(direction[1],direction[2])
    if YZAngle>math.pi/2:
        YZAngle -=math.pi/2
    elif YZAngle<-math.pi/2:
        YZAngle+=math.pi/2
    XZAngle = math.atan2(direction[0],direction[2])
    return (YZAngle,XZAngle,0)