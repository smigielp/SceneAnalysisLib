'''
Created on 23 mar 2017

@author: Mateusz Raczynski
'''
import numpy as np

import Utils


class Object3d(object):
    def __init__(self,vertices=None,uvs=None,normals=None,faces=None):
        self.name = None
        self.vertexArray = vertices
        self.UVCoordinatesArray = uvs
        self.NormalsArray = normals
        self.facesArray = faces
        self.elements = None
        if self.vertexArray is not None and self.facesArray is not None:
            self.buildObject()

    def buildObject(self):
        self.elements = []
        if self.NormalsArray is not None and len(self.NormalsArray) > 0 and\
                        len(self.NormalsArray) != len(self.vertexArray):
            self.buildWithNormalArray()
        else:
            self.build()
        self.elements = np.array(self.elements)

    def build(self):
        for face in self.facesArray:
            if face[0][0]==-1 or face[0][1]==-1 or face[0][2]==-1:
                continue
            self.elements.append(face[0][0])
            self.elements.append(face[0][1])
            self.elements.append(face[0][2])

    def buildWithNormalArray(self):
        self.tempNormalArray = []
        self.tempVertexArray = []

        for face in self.facesArray:
            if not self.faceHasNormals(face):
                print "Invalid face, ",face
                continue
            for i in range(0,2):
                v = self.vertexArray[face[0][i]]
                n = self.NormalsArray[face[2][i]]
                f = self.findSimilarVertex(v,n)
                if f==-1:
                    self.tempVertexArray.append(v)
                    self.tempNormalArray.append(n)
                    self.elements.append(len(self.tempVertexArray)-1)
                else:
                     self.elements.append(i)
        self.vertexArray = Utils.getNumpyArray(self.tempVertexArray)
        self.NormalsArray = Utils.getNumpyArray(self.tempNormalArray)
        self.tempVertexArray = None
        self.tempNormalArray = None

    def faceHasNormals(self, face):
        return not (face[2][0]==-1 or face[2][1]==-1 or face[2][2]==-1)

    def findSimilarVertex(self,vertex,normal):
        i = 0
        for v in self.tempVertexArray:
            dist = np.linalg.norm(vertex - v)
            if i >= len(self.tempNormalArray):
                break
            distn = np.linalg.norm(self.tempNormalArray[i] - normal)
            if dist < 0.00001 and distn < 0.00001:
                return i
            i+=1
        return -1

    def verify(self):
        for ele in self.elements:
            found = False
            i=0
            for ver in self.vertexArray:
                if(ele==i):
                    found = True
                    break
                i+=1
            if not found:
                assert(found)

def loadObjectFromObjFile(path,splitObjects=False):
    objFile = open(path, 'r')

    objectsList = []
    VertexList = []
    UVCoordinatesList = []
    NormalsList = []
    facesList = []
    currObject = None

    totalVertexCount = 0
    totalTextureCount = 0
    totalNormalsCount = 0
    totalFaceCount = 0

    prevVertexCount = 0
    currVertexCount = 0
    vertexCount = 0
    prevNormalsCount = 0
    currNormalsCount = 0
    normalsCount = 0
    #todo: count texture coordinates
    for line in objFile:
        split = line.split()
        if not len(split):
            continue
        if split[0] == "g": #model name
            if splitObjects:
                vertexArray = np.array(VertexList,dtype=np.float32)
                textureArray = np.array(UVCoordinatesList,dtype=np.float32)
                normalsArray = np.array(NormalsList,dtype=np.float32)
                faceArray = np.array(facesList,dtype=np.int32)
                totalVertexCount += len(vertexArray)
                totalTextureCount += len(textureArray)
                totalNormalsCount += len(normalsArray)
                totalFaceCount += len(faceArray)

                if currObject is not None:
                    currObject.facesArray = faceArray
                    currObject.buildObject()
                    currObject.verify()
                    objectsList.append(currObject)
                    prevVertexCount = prevVertexCount+currVertexCount
                    prevNormalsCount = prevNormalsCount+currNormalsCount

                currVertexCount = vertexCount
                vertexCount = 0
                currNormalsCount = normalsCount
                normalsCount = 0
                currObject = Object3d(vertexArray,textureArray,normalsArray,None)

                if len(split)>1:
                    currObject.name = split[1]
                VertexList = []
                UVCoordinatesList = []
                NormalsList = []
                facesList = []
        elif split[0] == "s":   # smoothgroup
            pass
        elif split[0] == "mtllib": #materials lib
            pass
        elif split[0] == "usemtl": #materal use
            pass
        elif split[0] == "v": #vertex
            vertexCount+=1
            vertex = split[1:]
            npVertex = np.array(vertex,dtype=np.float)
            VertexList.append(npVertex)
        elif split[0] == "vn": #normal
            normalsCount+=1
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
                face[0][count-1] = int(removeSlash[0])-1-prevVertexCount
                if removeSlash[1] == "":
                    face[1][count - 1] = -1
                else:
                    face[1][count-1] = int(removeSlash[1])-1
                if len(removeSlash)>2:
                    if removeSlash[2] == "":
                        face[2][count - 1] = -1
                    else:
                        face[2][count-1] = int(removeSlash[2])-1-prevNormalsCount
                count += 1
            facesList.append(face)
        elif split[0] == "#" or split[0][0] == '#': #special
            continue

    if not splitObjects:
        totalVertexCount = len(VertexList)
        totalTextureCount = len(UVCoordinatesList)
        totalNormalsCount = len(NormalsList)
        totalFaceCount = len(facesList)

    print ("Total vertices: " + str(totalVertexCount))
    print ("Total texture coordinates: " + str(totalTextureCount))
    print ("Total normals: " + str(totalNormalsCount))
    print ("Total faces: " + str(totalFaceCount))

    objFile.close()

    vertexArray = np.array(VertexList, dtype=np.float32)
    textureArray = np.array(UVCoordinatesList, dtype=np.float32)
    normalsArray = np.array(NormalsList, dtype=np.float32)
    faceArray = np.array(facesList, dtype=np.int32)
    if splitObjects:
        currObject.facesArray = faceArray
        currObject.buildObject()
        currObject.verify()
        objectsList.append(currObject)
    VertexList = []
    UVCoordinatesList = []
    NormalsList = []
    facesList = []

    if splitObjects:
        return objectsList
    return Object3d(vertexArray,textureArray,normalsArray,faceArray)

