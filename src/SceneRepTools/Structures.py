import ModelBuilder3D
from Tools import Utils as utl
from Tools import GnuplotDrawer
from Tools import Utils
from copy import deepcopy


###############################################################################################
# The set of classes to collect information about scene elements
# 
# Overview of classes
# - ProjectionSet -  class holding information about complete set of projections
#                    used by 3D model building algotithm
#


class ProjectionSet(object):
    
    def __init__(self, topProjection, topFeatures, wallsProjectionsList):
        self.top = topProjection
        self.topFeatures = topFeatures
        self.wallsProjections = wallsProjectionsList
        self.front = None
        self.right = None
        for projection in self.wallsProjections:
            angle = projection[2]
            if angle == 0:
                self.front = projection[0]
                self.frontFeatures = projection[1]
            elif angle == 0.5:
                self.right = projection[0]
                self.rightFeatures = projection[1]
        if self.front is None or self.right is None:
            raise 'Niekompletny zestaw rzutow. Nie mozna wygenerowac bryly 3D'  


    def standardiseMainProjections(self):        
        topMaxY = utl.getMaxPoint(self.top, 1)[1]
        frontMinY = utl.getMinPoint(self.front, 1)[1]
        rightMaxX = utl.getMaxPoint(self.right, 0)[0]
        rightMinY = utl.getMinPoint(self.right, 1)[1]
        rightMinX = utl.getMinPoint(self.right, 0)[0]
        
        frontMaxX = utl.getMaxPoint(self.front, 0)[0]
        frontMinX = utl.getMinPoint(self.front, 0)[0]
        topMaxX = utl.getMaxPoint(self.top, 0)[0]
        topMinX = utl.getMinPoint(self.top, 0)[0]
        topMinY = utl.getMinPoint(self.top, 1)[1]
                                
        topHeight = topMaxY - topMinY
        
        rightWidth = rightMaxX - rightMinX        
        scaleRight = topHeight / rightWidth
        
        frontWidth = frontMaxX - frontMinX
        topWidth = topMaxX - topMinX
        scaleFront = topWidth / frontWidth    
        
        # normalizacja rzutow by odpowiadaly sobie skala i polozeniem 
        for pt in self.front:
            pt[0] = (pt[0] - frontMinX) * scaleFront + topMinX 
            
        for pt in self.right:
            pt[0] = (pt[0] - rightMinX) * scaleRight + topMinY  
            pt[1] = (pt[1] - rightMinY) * scaleRight + frontMinY 
     
             
    ########################################################################################
    # Procedura tymczasowa. Trzeba przerobic
    #
    def sweepFeatures(self):
        frontMinY = utl.getMinPoint(self.front, 1)[1]
        frontMaxY = utl.getMaxPoint(self.front, 1)[1]
        sweepedFeatures = []
        for feature in self.topFeatures:
            sweepedFeatures.append(ModelBuilder3D.sweepFeature(feature, 0, 1, 2, frontMinY, frontMaxY))
        self.topSweepedFeatures = sweepedFeatures
        
        topCenterPoint = Utils.getWeightCenter(self.top) + [0]
                
        for proj in self.wallsProjections:
            features = proj[1]
            angle = proj[2]
            topRotated = utl.rotateVertexByCenterPoint(self.top, topCenterPoint, -angle)
                                                
            topMaxX = utl.getMaxPoint(topRotated, 0)[0]
            topMinX = utl.getMinPoint(topRotated, 0)[0]
            topMaxY = utl.getMaxPoint(topRotated, 1)[1]
            topMinY = utl.getMinPoint(topRotated, 1)[1]
                                    
            topWidth = topMaxX - topMinX
            
            sweepedFeatures = []
            for feature in features:
                minX = utl.getMinPoint(feature, 0)[0]
                maxX = utl.getMaxPoint(feature, 0)[0]
                minY = utl.getMinPoint(feature, 1)[1]
                width = maxX - minX
                scale = topWidth / width
                for pt in self.right:
                    pt[0] = (pt[0] - minX) * scale + topMinY  # ((pt[0] - (rightMinX - topMinY)) - rightMinX) * scaleRight + rightMinX
                    pt[1] = (pt[1] - minY) * scale + frontMinY  # ((pt[1] - (rightMinY - frontMinY)) - rightMinY) * scaleRight + rightMinY
                
                sweeped = ModelBuilder3D.sweepFeature(feature, 0, 2, 1, topMaxY, topMinY)
                for i in range(len(sweeped.sideWalls)):
                    # print '-------'
                    # print wall
                    sweeped.sideWalls[i] = utl.rotateVertexByCenterPoint(sweeped.sideWalls[i], topCenterPoint, angle)
                    # print wall
                sweepedFeatures.append(sweeped)
            proj.append(sweepedFeatures)
      
      
                              
#############################################################################################
# Class holding information bout sigle fearure (hole, indepth) in wall of 3D model
# @shape3D    - shape of hole in wall
# @sideWalls  - walls marking boudaries of hole inside 3D model
#
class Feature(object):
    
    def __init__(self, shape3D, walls3D):
        self.shape = shape3D
        self.sideWalls = walls3D
        

#############################################################################################
# Class holding a group of walls (laying on the same plane) in 3D model
# with the set of features
#
class WallStructure(object):
    
    def __init__(self, projection2D, createdWalls3D, angleToFront, features3D):
        self.projection = projection2D
        self.walls = createdWalls3D
        self.angleToFront = angleToFront
        self.features = features3D


##############################################################################################
# Class holding information about whole 3D model of an object
#
class ShapeStructure(object):
    
    def __init__(self, wallStructures=[], domain3D=[]):
        self.wallStructures = wallStructures
        self.domain = domain3D
        
        
    def addWall(self, projection2D, walls3D, angleToFront, features3D):
        wallStruct = WallStructure(projection2D, walls3D, angleToFront, features3D)
        self.wallStructures.append(wallStruct)
        
        
    def showWalls3D(self, mode=Utils.VECTOR_MODE, projectionId=None):
        vectors3D = []
        if projectionId is None:
            for wallStruct in self.wallStructures:
                vectors3D.extend(wallStruct.walls)
        else:
            vectors3D.extend(self.wallStructures[projectionId].walls)
        if mode == Utils.ARROW_MODE:
            GnuplotDrawer.printArrowPicture(vectors3D, self.domain)
        elif mode == Utils.VECTOR_MODE:
            GnuplotDrawer.printVectorPicture(vectors3D, self.domain)
        else:
            print 'Log: ShowWalls3D - Wrong print mode', mode
        
        
    def showFeatures3D(self, mode=Utils.VECTOR_MODE, featureId=None):
        vectors3D = []
        if featureId is None:
            for wallStruct in self.wallStructures:
                for feature in wallStruct.features:
                    vectors3D.extend(feature.sideWalls)
        else:
            vectors3D.extend(self.wallStructures[featureId].features)
        if mode == Utils.ARROW_MODE:
            GnuplotDrawer.printArrowPicture(vectors3D, self.domain)
        elif mode == Utils.VECTOR_MODE:
            GnuplotDrawer.printVectorPicture(vectors3D, self.domain)
        else:
            print 'Log: showFeatures3D - Wrong print mode', mode
      
            
    def showAll3D(self, mode=Utils.VECTOR_MODE):
        vectors3D = []
        for wallStruct in self.wallStructures:
            vectors3D.extend(wallStruct.walls)
            for feature in wallStruct.features:
                vectors3D.extend(feature.sideWalls)
        print vectors3D
        if mode == Utils.ARROW_MODE:
            GnuplotDrawer.printArrowPicture(vectors3D, self.domain)
        elif mode == Utils.VECTOR_MODE:
            GnuplotDrawer.printVectorPicture(vectors3D, self.domain)
        else:
            print 'Log: showAll3D - Wrong print mode', mode
     
     
    def getAllVectors(self):
        vectors3D = []    
        for wallStruct in self.wallStructures:
            vectors3D.extend(wallStruct.walls)
            for feature in wallStruct.features:
                vectors3D.extend(feature.sideWalls)
        return vectors3D
    
    


############################################################################################
# Class holding graph representation of the scene
#
class GraphStructure(object):  
     
    ########################################################################################
    # Creates structure holding 2D graph representation of the map.
    # Edges are created based on the nearest neighborhood
    # which is established with the range of nearest object
    #  
    def __init__(self, objectSet, domain, graphLevel):
        self.domain = domain
        self.objectSet = objectSet
        self.objectGraph = []
        for obj in self.objectSet:
            center = Utils.getCentroid(obj)
            closest = None
            dist = 1000000
            for nbr in self.objectSet:
                if nbr != obj:
                    tmpDist = Utils.getPointToVertexDist(center, nbr)
                    if tmpDist < dist:
                        closest = nbr
                        dist = tmpDist
            neighbourList = []
            # TODO - remove begin
            if closest is None:
                print 'WARNING. no closest element for: ', obj 
                continue
            # remove end
            for idx, nbr in enumerate(self.objectSet):
                if nbr != obj:
                    if Utils.getPointToVertexDist(center, nbr) < Utils.getPointToVertexFarDist(center, closest):
                        neighbourList.append([nbr, Utils.getCentroid(nbr), idx])
            
            self.objectGraph.append([[obj, center], neighbourList])  
            
        if graphLevel == 2:
            tmpObjectGraph = []
            for idx, obj in enumerate(self.objectGraph):
                tmpObj = deepcopy(obj)
                for nbr in obj[1]:
                    # nbr[2] - indeks obiektu w zbiorze i grafie
                    # self.objectGraph[nbr[3]][1] - tablica z sasiadami obiektu
                    tmpObj[1].extend([tmpNbr for tmpNbr in self.objectGraph[nbr[2]][1] if tmpNbr[2] != idx ])
                tmpObjectGraph.append(tmpObj)
            self.objectGraph = tmpObjectGraph
                        
    
    
    def getGraphElement(self, idx):
        return self.objectGraph[idx]
    
    def getGraph(self):
        return self.objectGraph

    def getDomain(self):
        return self.domain
    
    def printGraph(self):
        for obj in self.objectGraph[0:2]:
            print obj

