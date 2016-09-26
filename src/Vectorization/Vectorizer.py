from Tools import GnuplotDrawer
from Tools import Utils
from copy import deepcopy


BACKGROUND_POINT = 0
FIGURE_POINT = 255
MARKED_POINT = 2


###########################################################################################
# Class with vectorisation methods. Vectorisation process takes matrix of [0, 1] values 
# where "1" marks area of object being vectorised and "0" marks the backgroung
# 

class Vectorizer(object):
    
    def __init__(self, cornerAngle=0, windowSize=0, debugLevel=0):
        self.debugLevel = debugLevel
        # angle between following vertex elements which are treated as corner
        self.setParameters(windowSize)
          
    
    def setParameters(self, windowSize): 
        self.winSize = windowSize
        self.window = []
        radius = int(self.winSize / 2)
        self.radius = radius
        # construction of "window" used for search of following points on the object's contour
        tmp = range(-radius, radius)
        for i in tmp:
            self.window.append([-radius, i])
        for i in tmp:
            self.window.append([i, radius])
        tmp = range(-radius + 1, radius + 1)
        tmp.reverse()
        for i in tmp:
            self.window.append([radius, i])
        for i in tmp:
            self.window.append([i, -radius]) 
        self.window = self.window + self.window
              
            
    
    ############################################################################################   
    # based on matrix of [0, 1] values creates lists of points marking the objects' contours
    #
    def getBorderPointSequence(self, image, borderPointsExtraction):
        self.fullPicturePoints = []
        self.minFrameX = self.radius
        self.maxFrameX = image.shape[0] - self.radius
        self.minFrameY = self.radius
        self.maxFrameY = image.shape[1] - self.radius
        i = self.radius
        while i < self.maxFrameX:
            j = self.radius            
            while j < self.maxFrameY:
                # exiting currently processed contour (end of contour)
                if image.item(i, j) == MARKED_POINT:
                    while j < self.maxFrameY and image.item(i, j) in (MARKED_POINT, FIGURE_POINT):
                        j += 1
                if j < self.maxFrameY and image.item(i, j) == FIGURE_POINT: 
                    # print 'START NEW FIGURE'
                    # list collecting points where vertex forks
                    self.splittingPoints = []                    
                    self.singleObjectPoints = []                    
                    borderPointsExtraction(self, image, i, j)                    
                    self.fullPicturePoints.append(self.singleObjectPoints)
                    break
                j += 1
            i += 1
        return self.fullPicturePoints
    
        
     
    ############################################################################################
    # Set of functions for extracting objects contours based on objects pictures 
    # after process of border extraction (areas inside objects are empty, marked with "0")
    #
    def extractBorderedObject(self, image, i, j): 
        # self.prevPoint = None
        followingPoints = self.getFollowingPoints(image, i, j)
        while followingPoints != []:
            self.splittingPoints.extend(followingPoints[1:])
            i_1 = followingPoints[0][0]
            j_1 = followingPoints[0][1]            
            followingPoints = self.getFollowingPoints(image, i_1, j_1)
        #try:
            # When the border forks, method follows the branch
            #p = self.splittingPoints[0]
            #self.splittingPoints = self.splittingPoints[1:]
            #self.getSingleObjectPoints(image, p[0], p[1], True)
        #except:
            #pass
        
     
    ############################################################################################
    # Searching following points on the border
    # There can be more points when the border line forks
    # @return: list of points on border
    def getFollowingPoints(self, image, i, j, begin=False):
        self.singleObjectPoints.append([i, j])
        followingPoints = []
        x = 0    
        # If first element of "window" is located on the border line - exiting line by going counter clockwise
        while x > -len(self.window) + 1 and image.item(i + self.window[x][0], j + self.window[x][1]) == FIGURE_POINT:
            x -= 1
        while x < len(self.window) - 1:
            x += 1
            try: 
                if i > 0 and j > 0 and image.item(i + self.window[x][0], j + self.window[x][1]) == FIGURE_POINT:                
                    beg = x
                    while x < len(self.window) - 1 and image.item(i + self.window[x][0], j + self.window[x][1]) == FIGURE_POINT:
                        x += 1
                    end = x - 1
                    middle = (beg + end) / 2
                    # middle = end
                    i_1 = i + self.window[middle][0]
                    j_1 = j + self.window[middle][1]
                    followingPoints.append([i_1, j_1]) 
            except:
                return []
        # Marking current "window" area as already searched
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                if image.item(i + x, j + y) == FIGURE_POINT:
                    image.itemset(i + x, j + y, MARKED_POINT)
        return followingPoints
    
    
    
    
    ############################################################################################
    ############################################################################################    
    
    def makeSmooth(self, objects, outlierDist):
        return self.makeSmoothRDP(objects, outlierDist)
    
    
    def makeSmoothRDP(self, objects, outlierDist):
        vectors = []
        for pointList in objects:
            smoothVectors = self.removeRedundantRDP(pointList, outlierDist)
            print "Dist", Utils.getDistance(smoothVectors[0], smoothVectors[-1])
            if Utils.getDistance(smoothVectors[0], smoothVectors[-1]) < outlierDist*3:                
                smoothVectors[-1] = deepcopy(smoothVectors[0])
            vectors.append(smoothVectors)
        self.finalPoints = vectors        
        return self.finalPoints
    
    # Ramer-Douglas-Peuker algorithm implementation
    def removeRedundantRDP(self, pointList, epsilon):        
        dmax = 0
        index = 0
        end = len(pointList)-1
        for i in range(1, end - 1):
            d = Utils.getPointToLineDist(pointList[0], pointList[end], pointList[i])
            if d > dmax:
                index = i
                dmax = d
        # If max distance is greater than epsilon, recursively simplify
        if dmax > epsilon:
            # Recursive call
            recResults1 = self.removeRedundantRDP(pointList[0 : index], epsilon)
            recResults2 = self.removeRedundantRDP(pointList[index : end+1], epsilon)
                 
            # Build the result list
            resultList = recResults1[0 : len(recResults1)-1] + recResults2[0 : len(recResults2)]
        else:
            resultList = [pointList[0], pointList[end]]
        
        return resultList
    
       
    
    def vectorPostProcessing(self, lines, combThreshold=8, straightThreshold=5, postProcLevel=4):
        if postProcLevel > 0:
            self.combineCloseVectors(lines, combThreshold)
            if self.debugLevel > 1:
                GnuplotDrawer.printVectorPicture(lines, self.domain)       
        if postProcLevel > 1:
            self.straightenVectors(lines, straightThreshold)
        return lines
    
    
    ############################################################################################
    # V.1. - for vectorMode = False
    #      - checks only if first and last point are close (without intermediate points)
    def combineCloseVectors(self, lines, threshold):
        i = 0
        for line in lines:
            if len(line) > 2 and Utils.getDistance(line[0], line[-1]) < threshold:
                line.append(deepcopy(line[0]))
        while i < len(lines):
            line1 = lines[i]
            if line1[0] == line1[-1] or len(line1) < 1:
                i += 1
                continue
            j = i + 1
            wasCombined = False
            while j < len(lines):
                line2 = lines[j]
                if line2[0] == line2[-1] or len(line2) < 1:
                    j += 1
                    continue
                if Utils.getDistance(line1[0], line2[0]) < threshold:
                    # Attaching reversed line2 to the beginning of line1
                    line2.reverse()
                    line1 = line2 + line1
                    lines[i] = line1
                    lines.pop(j)
                    wasCombined = True
                elif Utils.getDistance(line1[0], line2[-1]) < threshold:
                    # Attaching line2 to the beginning of line1
                    line1 = line2 + line1
                    lines[i] = line1
                    lines.pop(j)
                    wasCombined = True
                elif Utils.getDistance(line1[-1], line2[0]) < threshold:
                    # Attaching line2 to the end of line1
                    line1 = line1 + line2
                    lines[i] = line1
                    lines.pop(j)
                    wasCombined = True
                elif Utils.getDistance(line1[-1], line2[-1]) < threshold:
                    # Attaching reversed line2 to the end of line1
                    line2.reverse()
                    line1 = line1 + line2
                    lines[i] = line1
                    lines.pop(j)
                    wasCombined = True
                j += 1
            # Switching to the next line only if nothing could be matched
            if not wasCombined:
                i += 1     
        # Closing the opened vertices
        for i in range(len(lines)):
            if Utils.getDistance(lines[i][0], lines[i][-1]) < threshold:
                middlePoint = Utils.getMiddlePoint(lines[i][0], lines[i][-1])  
                lines[i][0] = deepcopy(middlePoint)
                lines[i][-1] = deepcopy(middlePoint)         
    
    
    ############################################################################################
    # Leveling the the vectors which are nearly horizontal or vertical
    def straightenVectors(self, lines, threshold):
        for vertex in lines:
            for i in range(len(vertex) - 1):
                if abs(vertex[i][0] - vertex[i + 1][0]) < threshold:
                    middleX = (vertex[i][0] + vertex[i + 1][0]) / 2.0
                    vertex[i][0] = vertex[i + 1][0] = middleX
                if abs(vertex[i][1] - vertex[i + 1][1]) < threshold:
                    middleY = (vertex[i][1] + vertex[i + 1][1]) / 2.0
                    vertex[i][1] = vertex[i + 1][1] = middleY
            # Leveling of the beginning and ending vectors
            crossing = Utils.getCrossingPoint(vertex[0], vertex[1], vertex[-1], vertex[-2])
            if crossing != None:
                vertex[0] = deepcopy(crossing)
                vertex[-1] = deepcopy(crossing)
                    
    
