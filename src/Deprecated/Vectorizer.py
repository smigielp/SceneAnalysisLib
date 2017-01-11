from Tools import GnuplotDrawer
from Tools import Utils
from copy import deepcopy


LINE_FINISH_MARKER = [-2, -2]

BACKGROUND_POINT = 0
FIGURE_POINT = 1
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
    def getBorderPointSequence(self, data2D, borderPointsExtraction):
        self.fullPicturePoints = []
        self.minFrameX = self.radius
        self.maxFrameX = len(data2D) - self.radius
        self.minFrameY = self.radius
        self.maxFrameY = len(data2D[0]) - self.radius
        i = self.radius
        while i < self.maxFrameX:
            j = self.radius            
            while j < self.maxFrameY:
                # exiting currently processed contour (end of contour)
                if data2D[i][j] == MARKED_POINT:
                    while j < self.maxFrameY and data2D[i][j] in (MARKED_POINT, FIGURE_POINT):
                        j += 1
                if j < self.maxFrameY and data2D[i][j] == FIGURE_POINT: 
                    # print 'START NEW FIGURE'
                    # list collecting points where vertex forks
                    self.splittingPoints = []                    
                    self.singleObjectPoints = []                    
                    borderPointsExtraction(self, data2D, i, j)                    
                    self.fullPicturePoints.append(self.singleObjectPoints)
                    print self.singleObjectPoints
                    break
                j += 1
            i += 1
        return self.fullPicturePoints
    
        
        
    ###############################################################################################
    ###############################################################################################
    ## Set of functions for extracting objects contours based on picture where area
    ## inside objects is filled (marked as "1")
    ##             
    
    def extractSolidObject(self, data, i, j):
        coord = [i, j]
        part = [coord]
        nextNbr = self.getNextNeighbour(data, part, coord)
        while(nextNbr != None):
            part.append(nextNbr)
            nextNbr = self.getNextNeighbour(data, part, nextNbr)
        part.append(LINE_FINISH_MARKER)
        self.singleObjectPoints = part
        
    
    def getNextNeighbour(self, data, pointSeq, coord):
        print coord
        i = len(self.window) / 2
        # when arrived at the beginning - exiting
        if len(pointSeq) > 3 and Utils.getDistance(pointSeq[0], coord) <= self.radius:
            return None
        # If the corner of searching "window" is placed outside object - searching clockwise
        # When inside - searching counter clockwise
        if data[coord[0] + self.window[i][0]][coord[1] + self.window[i][1]] == BACKGROUND_POINT:
            i += 1
            while i < len(self.window) and data[coord[0] + self.window[i][0]][coord[1] + self.window[i][1]] <> FIGURE_POINT:                
                i += 1
        else:      
            while i >= 0 and data[coord[0] + self.window[i-1][0]][coord[1] + self.window[i-1][1]] <> BACKGROUND_POINT:  # and i >= 0:
                i -= 1
        if i >= len(self.window) or i < 0 or data[coord[0] + self.window[i][0]][ coord[1] + self.window[i][1]] == MARKED_POINT :                             
            return None
        else:
            print len(self.window), i, coord[0] + self.window[i][0], coord[1] + self.window[i][1], data[coord[0] + self.window[i][0]][ coord[1] + self.window[i][1]]
            # marking current "window" area as already searched
            for x in range(-self.radius-1, self.radius + 1):
                for y in range(-self.radius-1, self.radius + 1):
                    if data[pointSeq[-1][0] + x][pointSeq[-1][1] + y] == FIGURE_POINT:
                        data[pointSeq[-1][0] + x][pointSeq[-1][1] + y] = MARKED_POINT
            return [coord[0] + self.window[i][0], coord[1] + self.window[i][1]]  
        
        
        
        
    ############################################################################################
    ############################################################################################
    ## Set of functions for extracting objects contours based on objects pictures 
    ## after process of bordering (areas inside objects are empty, marked with "0")
    ##
    def extractBorderedObject(self, data, i, j): 
        # self.prevPoint = None
        followingPoints = self.getFollowingPoints(data, i, j)
        while followingPoints != []:
            self.splittingPoints.extend(followingPoints[1:])
            i_1 = followingPoints[0][0]
            j_1 = followingPoints[0][1]            
            followingPoints = self.getFollowingPoints(data, i_1, j_1)
        # Marking the end of currently processed vertex
        self.singleObjectPoints.append(LINE_FINISH_MARKER)
        try:
            # When the border forks, method follows the branch
            p = self.splittingPoints[0]
            self.splittingPoints = self.splittingPoints[1:]
            self.getSingleObjectPoints(data, p[0], p[1], True)
        except:
            pass
        
     
    ############################################################################################
    # Searching following points on the border
    # There can be more points when the border line forks
    # @return: list of points on border
    def getFollowingPoints(self, data, i, j, begin=False):
        self.singleObjectPoints.append([i, j])
        followingPoints = []
        x = 0    
        # If first element of "window" is located on the border line - exiting line by going counter clockwise
        while x > -len(self.window) + 1 and data[i + self.window[x][0]][j + self.window[x][1]] == FIGURE_POINT:
            x -= 1
        while x < len(self.window) - 1:
            x += 1
            try: 
                if i > 0 and j > 0 and data[i + self.window[x][0]][j + self.window[x][1]] == FIGURE_POINT:                
                    beg = x
                    while x < len(self.window) - 1 and data[i + self.window[x][0]][j + self.window[x][1]] == FIGURE_POINT:
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
                if data[i + x][j + y] == FIGURE_POINT:
                    data[i + x][j + y] = MARKED_POINT
        return followingPoints
    
    
    ############################################################################################
    ############################################################################################
    
    
    def makeSmooth(self, objects, outlierDist):
        return self.makeSmooth2(objects, outlierDist)
        #return self.makeSmoothRDP(objects, outlierDist)
    
    def makeSmoothRDP(self, objects, outlierDist):
        vectors = []
        for pointList in objects:
            vectors.append(self.removeRedundantRDP(pointList, outlierDist))
        self.finalPoints = vectors        
        return self.finalPoints
    
    # Ramer-Douglas-Peuker algorithm implementation
    def removeRedundantRDP(self, pointList, epsilon):        
        dmax = 0
        index = 0
        end = len(pointList)
        for i in range(2, end - 1):
            d = Utils.getPointToLineDist(pointList[1], pointList[end], pointList[i])
            if d > dmax:
                index = i
                dmax = d
        # If max distance is greater than epsilon, recursively simplify
        if dmax > epsilon:
            # Recursive call
            recResults1 = self.removeRedundantRDP(pointList[1 : index], epsilon)
            recResults2 = self.removeRedundantRDP(pointList[index : end], epsilon)
     
            # Build the result list
            resultList = recResults1[1 : len(recResults1)-1] + recResults2[1 : len(recResults2)]
        else:
            resultList = [pointList[1], pointList[end]]
        
        return resultList
    
    
    def makeSmooth2(self, objects, outlierDist):
        vectors = []
        for vertex in objects:
            # print '=========='
            # print vertex
            if len(vertex) > 4:
                tmpVertex = []    
                i = 0
                while i < len(vertex) - 3:
                    i += 1
                    tmpVertex.append([-1, -1])
                    tmpVertex.append(vertex[i])      
                    # Detecting outliers              
                    if Utils.getPointToLineDist(vertex[i], vertex[i + 1], vertex[i + 2]) > outlierDist :
                        i += 1
                        tmpVertex.append(vertex[i])
                    else:
                        lineMarker = 2    
                        lastInLine = i + lineMarker
                        outliers = 0
                        k = i + lineMarker + 1
                        while k < len(vertex) :
                            if Utils.getPointToLineDist(vertex[i], vertex[i + lineMarker], vertex[k]) > outlierDist :
                                outliers += 1
                            else:
                                lastInLine = k
                            if outliers > 0:
                                i = lastInLine
                                tmpVertex.append(vertex[i])
                                break                                
                            k += 1
                        if k >= len(vertex):
                            tmpVertex.append(vertex[-1])
                            break
                                
                smoothVertex = []
                i = 1  # ommiting first [-1, -1] point, beginning and end of vertex is processed at later stage
                # print tmpVertex
                while i < len(tmpVertex):
                    if tmpVertex[i] == [-1, -1]:
                        point = Utils.getCrossingPoint(tmpVertex[i - 2], tmpVertex[i - 1], tmpVertex[i + 1], tmpVertex[i + 2])
                        
                        if point is not None and \
                           Utils.getDistance(point, tmpVertex[i - 1]) < 2 * self.winSize:
                            smoothVertex.append(point)
                        # elif Utils.getDistance(tmpVertex[i-1], tmpVertex[i-1]) < 2 * self.winSize:
                        else:
                            smoothVertex.append(Utils.getMiddlePoint(tmpVertex[i - 1], tmpVertex[i + 1]))
                    i += 1
                # Closing the vertex when first and last point are close
                if Utils.getDistance(tmpVertex[-1], tmpVertex[1]) < 2 * self.winSize and len(tmpVertex) > 3:
                    point = Utils.getCrossingPoint(tmpVertex[-2], tmpVertex[-1], tmpVertex[1], tmpVertex[2])
                    smoothVertex.insert(0, point)   
                    smoothVertex.append(deepcopy(point))      
                # If vertex is opened then adding first and last element
                else:
                    smoothVertex.insert(0, tmpVertex[1])
                    smoothVertex.append(tmpVertex[-1])
                # print smoothVertex
                vectors.append(smoothVertex)
                #print '----', smoothVertex
        self.finalPoints = vectors        
        return self.finalPoints
    
    
    ############################################################################################
    # @param objects: list of separate vertices (each vertex is a sequence of points)
    #
    def makeSmoothNew(self, objects, outlierDist):
        vectors = []
        # dla kazdej lamanej v
        for vertex in objects:
            if len(vertex) > 4:
                smoothVertex = []                    
                
                i = 0
                while i < len(vertex):
                    
                    smoothVertex.append(vertex[i])                    
                    k = i + 2
                    lastInLine = i + 1
                    outliers = 0
                    while k < len(vertex) :
                        if Utils.getPointToLineDist(vertex[i], vertex[i + 1], vertex[k]) > outlierDist :
                            outliers += 1
                        else:
                            lastInLine = k
                        if outliers > 0:
                            i = lastInLine
                            break
                        k += 1
                    if k >= len(vertex):
                        break
                
                vectors.append(smoothVertex)
                
        self.finalPoints = vectors        
        return self.finalPoints

    
    
    def vectorPostProcessing(self, lines, combThreshold=8, angleThreshold=0.1, remShortThreshold=8, straightThreshold=5, postProcLevel=4):
        if postProcLevel > 0:
            self.combineCloseVectors(lines, combThreshold)
            if self.debugLevel > 1:
                GnuplotDrawer.printVectorPicture(lines, self.domain)
            
        #if postProcLevel > 1:
        #    self.combineVectorsOnSingleLine(lines, angleThreshold)        
        #    if self.debugLevel > 1:
        #        GnuplotDrawer.printVectorPicture(lines, self.domain)  
            
        #if postProcLevel > 2:
        #    self.removeShortVectors(lines, remShortThreshold)        
        #    if self.debugLevel > 1:
        #        GnuplotDrawer.printVectorPicture(lines, self.domain)             
                            
        if postProcLevel > 3:
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
                    # middlePoint = Utils.getMiddlePoint(line1[0], line2[0])
                    # line1[0] = middlePoint
                    line2.reverse()
                    # line1 = line2[:-1] + line1
                    line1 = line2 + line1
                    lines[i] = line1
                    lines.pop(j)
                    wasCombined = True
                elif Utils.getDistance(line1[0], line2[-1]) < threshold:
                    # Attaching line2 to the beginning of line1
                    # middlePoint = Utils.getMiddlePoint(line1[0], line2[-1])
                    # line1[0] = middlePoint
                    # line1 = line2[:-1] + line1
                    line1 = line2 + line1
                    lines[i] = line1
                    lines.pop(j)
                    wasCombined = True
                elif Utils.getDistance(line1[-1], line2[0]) < threshold:
                    # Attaching line2 to the end of line1
                    # middlePoint = Utils.getMiddlePoint(line1[-1], line2[0])
                    # line1[-1] = middlePoint
                    # line1 = line1 + line2[1:]
                    line1 = line1 + line2
                    lines[i] = line1
                    lines.pop(j)
                    wasCombined = True
                elif Utils.getDistance(line1[-1], line2[-1]) < threshold:
                    # Attaching reversed line2 to the end of line1
                    # middlePoint = Utils.getMiddlePoint(line1[-1], line2[-1])
                    # line1[-1] = middlePoint
                    line2.reverse()
                    # line1 = line1 + line2[1:]
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
                # middlePoint = lines[i][0] 
                middlePoint = Utils.getMiddlePoint(lines[i][0], lines[i][-1])  
                lines[i][0] = deepcopy(middlePoint)
                lines[i][-1] = deepcopy(middlePoint)
    
    
    ############################################################################################
    # Iteratively following the vertex adding short segments to the adjacent one
    # Continues from the beginning until the short segment is found
    def removeShortVectors(self, lines, threshold):
        for line in lines:
            if len(line) == 2 and Utils.getDistance(line[0], line[1]) < threshold:
                lines.remove(line)
            elif len(line) > 2:
                if Utils.getDistance(line[0], line[1]) < threshold:
                    # tmpPoint = Utils.getCrossingPoint(line[-2], line[-1], line[1], line[2])
                    tmpPoint = Utils.getMiddlePoint(line[0], line[1])
                    line[-1] = deepcopy(tmpPoint)
                    line[0] = deepcopy(tmpPoint)
                    line.pop(1)
                if Utils.getDistance(line[-2], line[-1]) < threshold:
                    # tmpPoint = Utils.getCrossingPoint(line[-3], line[-2], line[0], line[1])
                    tmpPoint = Utils.getMiddlePoint(line[-2], line[-1])
                    line[-1] = deepcopy(tmpPoint)
                    line[0] = deepcopy(tmpPoint)
                    line.pop(-2)
                removedLines = True
                while removedLines:
                    i = 1
                    removedLines = False
                    while i < len(line) - 2:
                        if Utils.getDistance(line[i], line[i + 1]) < threshold:
                            if Utils.getDistance(line[i - 1], line[i]) > 1.5 * threshold and \
                               Utils.getDistance(line[i + 1], line[i + 2]) > 1.5 * threshold:
                                tmpPoint = Utils.getCrossingPoint(line[i - 1], line[i], line[i + 1], line[i + 2])
                            else:
                                tmpPoint = Utils.getMiddlePoint(line[i], line[i + 1])
                            line[i] = tmpPoint
                            line.pop(i + 1)
                            removedLines = True
                        else:
                            i += 1
    
    
    def combineVectorsOnSingleLine(self, lines, threshold):
        x = 0
        while x < len(lines):
            line = lines[x]
            if len(line) > 2:
                j = 2
                ptsToRemove = []
                while j < len(line):
                    angle1 = Utils.getLineAngle(line[j - 2], line[j - 1])
                    angle2 = Utils.getLineAngle(line[j - 1], line[j])
                    
                    if abs(angle1 - angle2) < threshold:
                        ptsToRemove.append(j - 1)
                    # while j < len(line)-1 and abs(angle1 - angle2) < threshold:
                    #    ptsToRemove.append(j-1)                 
                    #    j += 1   
                    #    angle1 = Utils.getLineAngle(line[i], line[i+1])
                    #    angle2 = Utils.getLineAngle(line[j-1], line[j])    
                    
                        # j += 1
                        # print line[i], line[i+1], ' -> ', angle1
                        # print line[i], line[j], ' -> ', angle2
                        # print '------'
                    j += 1
                
                
                lines[x] = [line[i] for i in range(len(line)) if i not in ptsToRemove]
                # Checking if first and last vector lies on single line
                angle1 = Utils.getLineAngle(lines[x][0], lines[x][1])
                angle2 = Utils.getLineAngle(lines[x][-2], lines[x][-1])
                if abs(angle1 - angle2) < threshold:
                    lines[x].pop()
                    lines[x][0] = deepcopy(lines[x][-1])
            x += 1                
    
    def combineVectorsOnSingleLine__OLD(self, lines, threshold):
        x = 0
        while x < len(lines):
            line = lines[x]
            if len(line) > 2:
                i = 0
                j = 2
                ptsToRemove = []
                while j < len(line):
                    angle1 = Utils.getLineAngle(line[i], line[i + 1])
                    angle2 = Utils.getLineAngle(line[j - 1], line[j])
                    
                    if abs(angle1 - angle2) < threshold:
                        ptsToRemove.append(j - 1)
                    # while j < len(line)-1 and abs(angle1 - angle2) < threshold:
                    #    ptsToRemove.append(j-1)                 
                    #    j += 1   
                    #    angle1 = Utils.getLineAngle(line[i], line[i+1])
                    #    angle2 = Utils.getLineAngle(line[j-1], line[j])    
                    
                        # j += 1
                        # print line[i], line[i+1], ' -> ', angle1
                        # print line[i], line[j], ' -> ', angle2
                        # print '------'
                    i = j - 1
                    j += 1
                
                # Checking if first and last vector lies on single line
                angle1 = Utils.getLineAngle(lines[x][0], lines[x][1])
                angle2 = Utils.getLineAngle(lines[x][-2], lines[x][-1])
                if abs(angle1 - angle2) < threshold:
                    lines[x].pop()
                    lines[x][0] = deepcopy(lines[x][-1])
                lines[x] = [line[i] for i in range(len(line)) if i not in ptsToRemove]
            x += 1                
    
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
                    
    
