'''
Created on 23 mar 2017

@author: Mateusz Raczynski
'''
import numpy as np


class Object3d(object):
    def __init__(self,vertices=None,uvs=None,normals=None,faces=None):
        self.vertexArray = vertices
        self.UVCoordinatesArray = uvs
        self.NormalsArray = normals
        self.facesArray = faces
        self.elements = None
        if self.vertexArray is not None and self.facesArray is not None:
            self.buildObject()

    def buildObject(self):
        self.elements = []
        for face in self.facesArray:
            if face[0][0]==-1 or face[0][1]==-1 or face[0][2]==-1:
                continue
            self.elements.append(face[0][0])
            self.elements.append(face[0][1])
            self.elements.append(face[0][2])
        self.elements = np.array(self.elements)


def loadObjectFromObjFile(path,splitObjects=False):
    objFile = open(path, 'r')

    objectsList = []
    VertexList = []
    UVCoordinatesList = []
    NormalsList = []
    facesList = []
    for line in objFile:
        split = line.split()
        if not len(split):
            continue
        if split[0] == "g": #model name
            #todo: split if there are multiple objects in file and if necessary
            if splitObjects and len(facesList)>0:
                vertexArray = np.array(VertexList,dtype=np.float32)
                textureArray = np.array(UVCoordinatesList,dtype=np.float32)
                normalsArray = np.array(NormalsList,dtype=np.float32)
                faceArray = np.array(facesList,dtype=np.int32)
                objectsList.append(Object3d(vertexArray,textureArray,normalsArray,faceArray))
                VertexList = []
                UVCoordinatesList = []
                NormalsList = []
                facesList = []
        elif split[0] == "s": #smoothgroup
            pass
        elif split[0] == "mtllib": #materials lib
            pass
        elif split[0] == "usemtl": #materal use
            pass
        elif split[0] == "v": #vertex
            vertex = split[1:]
            npVertex = np.array(vertex,dtype=np.float)
            VertexList.append(npVertex)
        elif split[0] == "vn": #normal
            normal = split[1:]
            npNormal = np.array(normal,dtype=np.float)
            NormalsList.append(npNormal)
        elif split[0] == "vt": #uv coordinate
            uvtext = split[1:]
            npUvtext = np.array(uvtext,dtype=np.float)
            UVCoordinatesList.append(npUvtext)
        elif split[0] == "f": #face
            count = 1
            face = np.array([
                [-1,-1,-1],  #vertices
                [-1,-1,-1],  #uvs
                [-1,-1,-1]   #normals
            ],dtype=np.int16)
            while count < 4:
                removeSlash = split[count].split('/')
                if removeSlash[0] == "":
                    raise RuntimeError("File is corrupted.")
                face[0][count-1] = int(removeSlash[0])-1
                if removeSlash[1] == "":
                    face[1][count - 1] = -1
                else:
                    face[1][count-1] = int(removeSlash[1])-1
                if len(removeSlash)>2:
                    if removeSlash[2] == "":
                        face[2][count - 1] = -1
                    else:
                        face[2][count-1] = int(removeSlash[2])-1
                count += 1
            facesList.append(face)
        elif split[0] == "#" or split[0][0] == '#': #special
            continue

    vertexCount = len(VertexList)
    textureCount = len(UVCoordinatesList)
    normalsCount = len(NormalsList)
    faceCount = len(facesList)

    #todo: fix stats when there are multiple objects
    print ("Total vertices: " + str(vertexCount))
    print ("Total texture coordinates: " + str(textureCount))
    print ("Total normals: " + str(normalsCount))
    print ("Total faces: " + str(faceCount))

    objFile.close()

    vertexArray = np.array(VertexList, dtype=np.float32)
    textureArray = np.array(UVCoordinatesList, dtype=np.float32)
    normalsArray = np.array(NormalsList, dtype=np.float32)
    faceArray = np.array(facesList, dtype=np.int32)
    if splitObjects:
        objectsList.append(Object3d(vertexArray, textureArray, normalsArray, faceArray))
    VertexList = []
    UVCoordinatesList = []
    NormalsList = []
    facesList = []

    if splitObjects:
        return objectsList
    return Object3d(vertexArray,textureArray,normalsArray,faceArray)

def _extractObject(vertices,uvs,normals,faces):
    pass