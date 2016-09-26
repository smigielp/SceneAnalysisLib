import math
from copy import deepcopy
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.ops import linemerge
from Tools import GnuplotDrawer



#######################################################
# CONSTANTS
#######################################################
# Modes of controller action
VIDEO_CAPTURE = 0
STRUCTURE_BUILD_3D = 1
VECTORIZATION = 2
EXECUTE_COMPLEX_ACTION = 3

SOLID = 'SOLID'
BORDERED = 'BORDERED'

#######################################################
# Modes of printing vectors with Gnuplot
ARROW_MODE = 0
VECTOR_MODE = 1



############################################################################################
# Euclidean distance between two points
def getDistance(p1, p2):
    sum1 = 0
    for i in range(len(p1)):
        sum1 += abs(p1[i] - p2[i]) ** 2
    return math.sqrt(sum1)


def getPointToVertexDist(point, vertex):
    vtx = LineString(vertex)
    pt = Point(point)
    return pt.distance(vtx)

def getPointToVertexFarDist(point, vertex):
    dist = 0
    for pt in vertex:
        tmpDist = getDistance(point, pt)
        if tmpDist > dist:
            dist = tmpDist
    return dist


def getCentroid(vertex):
    vtx = LineString(vertex)
    return vtx.centroid.coords[0]
    

def getCapacity(p1, p2):
    cap = 1
    for i in range(len(p1)):
        cap *= abs(p1[i] - p2[i])
    return cap


def getSphereCapacity(radius):
    return math.pi * radius ** 2 


def getCapacity2(array):
    cap = 1
    for dim in array:
        cap *= abs(dim[1] - dim[0])
    return cap


def getMiddlePointXD(cube, dimension):
    return [(cube[0][j] + cube[1][j]) / 2.0 for j in range(dimension)]


def getMiddlePoint(p1, p2):
    return [(p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0]


def getMiddlePointByY(p1, p2, y):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    if y2 == y1:
        return None
    x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
    return x


def getWeightCenter(vertex):
    sumX = sumY = 0
    for point in vertex:
        sumX += point[0]
        sumY += point[1]
    return [sumX / len(vertex), sumY / len(vertex)]


############################################################################################
# wykonuje obrot punktu po pierwszych dwoch wspolrzednych
def rotate2D(point, center, alpha): 
    alpha = alpha * math.pi   
    point0 = [point[i] - center[i] for i in range(len(point))]
    newPoint = []
    newPoint.append(math.cos(alpha) * point0[0] - math.sin(alpha) * point0[1])
    newPoint.append(math.sin(alpha) * point0[0] + math.cos(alpha) * point0[1])
    if len(point0) == 3:
        newPoint.append(point0[2])
    for i in range(len(newPoint)):
        newPoint[i] += center[i]
    return newPoint


def getLineAngle(p1, p2):
    len1 = getDistance(p1, p2)
    lenX = p2[0] - p1[0]
    # lenY = p2[1] - p1[1]    
    if len1 == 0:
        return 0
    cosAlpha = lenX / len1
    alpha = math.acos(cosAlpha) / math.pi
    if p2[1] < p1[1]:
        alpha = 2 - alpha   
    return alpha


def getLineAngle2(p1, p2):
    return getAngle([0, 0], [0, 1], [p1, p2])


def getElem(data, coord):
    tmp = data[coord[0]]
    for i in range(1, len(coord)):
        tmp = tmp[coord[i]]
    return int(tmp)

def setElem(data, coord, val):
    tmp = data[coord[0]]
    for i in range(1, len(coord) - 1):
        tmp = tmp[coord[i]]
    tmp[coord[-1]] = val
 

############################################################################################    
# Returns distance of the point from line defined by two points (using Schwartz inequality)
# 
def getPointToLineDist(beg, end, point):
    lenA = getDistance(beg, end)    
    lenB = getDistance(beg, point)
    if lenA == 0:
        return lenB
    if lenB == 0:
        return 0
    scalar = 0.0
    for i in range(len(beg)):
        # with swap to the beginning of coordinates system
        scalar += (end[i] - beg[i]) * (point[i] - beg[i])
    cosAlpha = scalar / (lenA * lenB)
    cosAlpha = min(1.0, cosAlpha)
    alpha = math.acos(cosAlpha)
    distance = lenB * math.sin(alpha)
    return round(distance, 4)


def getPointToSegmentDist(beg, end, pt):
    spt = Point(pt)
    sline = LineString([beg, end])
    return sline.distance(spt)


def getAngle2(center, first, second):
    lenA = getDistance(center, first)    
    lenB = getDistance(center, second)
    if lenA == 0 or lenB == 0:
        return lenB
    scalar = 0.0
    for i in range(len(center)):
        # with swap to the beginning of coordinates system
        scalar += (first[i] - center[i]) * (second[i] - center[i])
    cosAlpha = scalar / (lenA * lenB)
    cosAlpha = min(0.999, max(-0.999, cosAlpha))
    alpha = math.acos(cosAlpha)    
    return alpha / math.pi


def getAngle(center, first, second):
    x1 = first[0] - center[0]
    y1 = first[1] - center[1]
    x2 = second[0] - center[0]
    y2 = second[1] - center[1]
    angle = math.atan2(y2, x2) - math.atan2(y1, x1)
    return (angle / math.pi) % 2


def getCrossingPoint2(p1, p2, p3, p4):
    line1 = LineString([p1, p2])
    line2 = LineString([p3, p4])
    point = line1.intersection(line2)
    print point
    return point

############################################################################################
# zwraca punkt przeciecie prostych wyznaczonych przez pary punktow
# @checkSegmentCrossing - dla "True" zwraca dodatkowa wartosc okreslajaca
#                         czy przecinaja sie tez odcinki wyznaczone przez pary punktow
def getCrossingPoint(p1, p2, p3, p4, checkSegmentCrossing=False):
    x = y = None
    if(p1[0] == p2[0] and p3[0] == p4[0] or
        p1[1] == p2[1] and p3[1] == p4[1]):
        return None  # p2 + [True] if checkSegmentCrossing else p2
    # pierwszy jest pionowo
    if p2[0] == p1[0]:
        x = p2[0]
        # drugi jest poziomo
        if p3[1] == p4[1]:
            y = p3[1]
        else:
            a2 = float(p3[1] - p4[1]) / float(p3[0] - p4[0])
            b2 = p3[1] - a2 * p3[0]
            y = a2 * x + b2
    # drugi jest pionowo
    if p3[0] == p4[0]:
        x = p3[0]
        # pierwszy jest poziomo
        if p2[1] == p1[1]:
            y = p2[1]
        else:
            a1 = float(p2[1] - p1[1]) / float(p2[0] - p1[0])
            b1 = p2[1] - a1 * p2[0]
            y = a1 * x + b1
    # pierwszy jest poziomo
    if p2[1] == p1[1]:
        y = p2[1]
        # drugi jest pionowo
        if p3[0] == p4[0]:
            x = p3[0]
        else:
            a2 = float(p3[1] - p4[1]) / float(p3[0] - p4[0])
            b2 = p3[1] - a2 * p3[0]
            x = (y - b2) / a2 
    # drugi jest poziomo
    if p3[1] == p4[1]:
        y = p3[1]
        if p2[0] == p1[0]:
            x = p2[0]
        else:
            a1 = float(p2[1] - p1[1]) / float(p2[0] - p1[0])
            b1 = p2[1] - a1 * p2[0]
            x = (y - b1) / a1
        
    if x != None and y != None:
        if checkSegmentCrossing:
            if (p1[0] <= x and x <= p2[0] or p2[0] <= x and x <= p1[0]) and \
               (p1[1] <= y and y <= p2[1] or p2[1] <= y and y <= p1[1]) and \
               (p3[0] <= x and x <= p4[0] or p4[0] <= x and x <= p3[0]) and \
               (p3[1] <= y and y <= p4[1] or p4[1] <= y and y <= p3[1]):
                return [x, y, True]
            else: 
                return [x, y, False]
        else:
            return [x, y]
    else:
        a1 = float(p2[1] - p1[1]) / float(p2[0] - p1[0]) 
        a2 = float(p3[1] - p4[1]) / float(p3[0] - p4[0])
        if a1 == a2:
            return p2 + [True] if checkSegmentCrossing else p2        
        
        b1 = float(p2[1] - a1 * p2[0])
        b2 = float(p3[1] - a2 * p3[0])
    
        y = float((a1 * b2 - a2 * b1) / (a1 - a2))
        x = float((y - b1) / a1)           
        if checkSegmentCrossing:
            if (p1[0] <= x and x <= p2[0] or p2[0] <= x and x <= p1[0]) and \
               (p1[1] <= y and y <= p2[1] or p2[1] <= y and y <= p1[1]) and \
               (p3[0] <= x and x <= p4[0] or p4[0] <= x and x <= p3[0]) and \
               (p3[1] <= y and y <= p4[1] or p4[1] <= y and y <= p3[1]):
                return [x, y, True]
            else: 
                return [x, y, False]
        else:
            return [x, y]

    
def getHausdorffDist(vertex1, vertex2):
    distV1 = 0
    for corner in vertex1:
        i = 1
        dist = 100000000
        while(i < len(vertex2)):
            dist = min(dist, getPointToLineDist(corner, vertex2[i - 1], vertex2[i]))  # czy na pewno ta funkcja
            i += 1
        distV1 = max(distV1, dist)
    distV2 = 0
    for corner in vertex2:
        i = 1
        dist = 100000000
        while(i < len(vertex1)):
            dist = min(dist, getPointToLineDist(corner, vertex1[i - 1], vertex1[i]))
            i += 1
        distV2 = max(distV2, dist)
    return max(distV1, distV2)


############################################################################################ 
# oblicza dlugosc lamanej okreslonej jako ciag punktow
def getVertexLen(vertex):
    i = 1
    llen = 0
    while i < len(vertex):
        llen += getDistance(vertex[i], vertex[i - 1])
        i += 1
    return llen


def getLongestVertex(multiList):
    llen = 0
    idx = 0
    for i, elist in enumerate(multiList):
        vlen = getVertexLen(elist)
        if vlen > llen:
            llen = vlen
            idx = i
    return multiList[idx]


def isPointInVertex(pt, vertex, x, y): 
    pt2D = [pt[x], pt[y]]
    spt = Point(pt2D)
    vertex2D = [[vpt[x], vpt[y]] for vpt in vertex]
    spol = Polygon(vertex2D)
    return spt.intersects(spol)



def getMaxPoint(vertex, dim=1):   
    maxPt = vertex[0]
    maxVal = 0
    for pt in vertex:
        if pt[dim] > maxVal:
            maxVal = pt[dim]
            maxPt = pt
    return maxPt


def getMinPoint(vertex, dim=1):
    minPt = vertex[0]
    minVal = 10000
    for pt in vertex:
        if pt[dim] < minVal:
            minVal = pt[dim]
            minPt = pt
    return minPt


############################################################################################
# pobiera liste najwyzej polozonych punktow bryly
# z dokladnoscia do distThreshold    
def getMaxYPointsIdx(vertex, distThreshold):
    maxPts = []
    maxPtsIdx = []
    maxVal = 0
    for pt in vertex:
        if pt[1] > maxVal:
            maxVal = pt[1]
    for i, pt in enumerate(vertex):
        if abs(maxVal - pt[1]) < distThreshold and pt not in maxPts:
            maxPts.append(pt)
            maxPtsIdx.append(i)
    return maxPtsIdx
    
    
############################################################################################
# pobiera liste najnizej polozonych punktow bryly
# z dokladnoscia do distThreshold   
def getMinYPointsIdx(vertex, distThreshold):
    minPts = []
    minPtsIdx = []
    minVal = 10000
    for pt in vertex:
        if pt[1] < minVal:
            minVal = pt[1]
    for i, pt in enumerate(vertex):
        if abs(minVal - pt[1]) < distThreshold and pt not in minPts:
            minPts.append(pt)
            minPtsIdx.append(i)
    return minPtsIdx


############################################################################################
# pobiera liste punktow polozonych najbardziej na prawo
# z dokladnoscia do distThreshold
def getMaxXPointsIdx(vertex, distThreshold):
    maxPts = []
    maxPtsIdx = []
    maxVal = 0
    for pt in vertex:
        if pt[0] > maxVal:
            maxVal = pt[0]
    for i, pt in enumerate(vertex):
        if abs(maxVal - pt[0]) < distThreshold and pt not in maxPts:
            maxPts.append(pt)
            maxPtsIdx.append(i)
    return maxPtsIdx


############################################################################################
# pobiera liste punktow polozonych najbardziej na lewo
# z dokladnoscia do distThreshold
def getMinXPointsIdx(vertex, distThreshold):
    minPts = []
    minPtsIdx = []
    minVal = 10000
    for pt in vertex:
        if pt[0] < minVal:
            minVal = pt[0]
    for i, pt in enumerate(vertex):
        if abs(minVal - pt[0]) < distThreshold and pt not in minPts:
            minPts.append(pt)
            minPtsIdx.append(i)
    return minPtsIdx


############################################################################################
# pobiera indeks punktu z listy indexes o najmniejszej
# wartosci X
def getMostLeftPoint(vertex, indexes):
    minVal = 100000
    minIdx = 0
    for i in indexes:
        if vertex[i][0] < minVal:
            minVal = vertex[i][0]
            minIdx = i
    return minIdx
    

def swapDimensions(listOfPoints, dimA, dimB):
    for point in listOfPoints:
        point[dimA], point[dimB] = point[dimB], point[dimA]
        
        
############################################################################################
# zwraca punkt posredni na odcinku dla podanej wspolrzednej (dowolnie wybranej)
def getMiddlePtCoord(ptA, ptB, coordKnownVal, coordKnown, coordCalc):
    if coordKnownVal > ptA[coordKnown] and coordKnownVal > ptB[coordKnown] or \
       coordKnownVal < ptA[coordKnown] and coordKnownVal < ptB[coordKnown] or \
       ptA[coordKnown] == ptB[coordKnown]:
        print 'Log: getMiddlePtCoord incorrect arguments - ', ptA, ptB, coordKnownVal, coordKnown, coordCalc 
    XX = ptB[coordCalc] - ptA[coordCalc]
    YY = ptB[coordKnown] - ptA[coordKnown]
    yy = ptB[coordKnown] - coordKnownVal
    xx = (XX / YY) * yy
    return ptB[coordCalc] - xx


############################################################################################  
# zwraca srodek ciezkosci zamknietej lamanej
def getCenterPoint(vertex):
    centerX = 0
    centerY = 0  
    for pt in vertex:
        centerX += pt[0]
        centerY += pt[1]
    return [centerX / len(vertex), centerY / len(vertex)]
    

def getVertexCrossing2(v1, v2, x, y, z, threshold=0):
    intersect = []
    
    #walls = v1 + v2
    #GnuplotDrawer.printVectorPicture(walls, [[200,700],[100,550],[150,400]])
    for wall1 in v1:
        if len(wall1) == 0:
            continue
        for wall2 in v2:
            if len(wall2) == 0:
                continue
            vcutA = deepcopy(wall1)
            vcutB = deepcopy(wall2)
            
            maxZ = getMaxPoint(vcutA, z)
            minZ = getMinPoint(vcutA, z)
            
            for i in range(len(vcutA)):
                vcutA[i] = [vcutA[i][x], vcutA[i][y]]
            for i in range(len(vcutB)):
                vcutB[i] = [vcutB[i][x], vcutB[i][y]]
            
            # HACK BEGIN- zorlaczanie bryl polacznonych pojedyncza linia. Mozna by przeniesc do osobnej funkcji
            # Usprawnienie: recznie usunac nakladajace sie odcinki u dolu i gory. Polaczyc powstale dziury odcinkami
            lineA = LineString(vcutA)
            multiA = lineA.intersection(lineA)
            
            if multiA.is_empty or multiA.geom_type == 'LineString':
                continue
            mergedA = linemerge(multiA)
            if mergedA.geom_type == 'MultiLineString':
                multiPolA = MultiPolygon([Polygon(elem) for elem in list(mergedA) if len(elem.coords[:]) > 2])
            else:
                multiPolA = MultiPolygon([Polygon(mergedA)])
                        
            lineB = LineString(vcutB)
            multiB = lineB.intersection(lineB)
                
            if multiB.is_empty or multiB.geom_type == 'LineString':
                continue
            mergedB = linemerge(multiB)
            if mergedB.geom_type == 'MultiLineString':
                multiPolB = MultiPolygon([Polygon(elem) for elem in list(mergedB) if len(elem.coords[:]) > 2])
            else:
                multiPolB = MultiPolygon([Polygon(mergedB)])
            # HACK END
            
            if not multiPolA.is_valid or not multiPolB.is_valid:
                continue
            intersectionPolygon = multiPolA.intersection(multiPolB)
            if intersectionPolygon.is_empty:
                continue
            
            print intersectionPolygon.geom_type
            if intersectionPolygon.geom_type == 'MultiPolygon':
                rawIntersect = [polygon.exterior.coords for polygon in intersectionPolygon]
            elif intersectionPolygon.geom_type == 'GeometryCollection': 
                rawIntersect = [] 
                for geom in intersectionPolygon:
                    try:
                        rawIntersect.extend([list(geom.exterior.coords)])
                    except:
                        print 'error extracting from GeometryCollections'
                        pass
            else:
                rawIntersect = [list(intersectionPolygon.exterior.coords)]
            
            for part in rawIntersect: 
                intersectPart = []
                for pt in part:
                    if minZ[z] == maxZ[z]:
                        ptCoordZ = minZ[z]
                    elif abs(minZ[x] - maxZ[x]) > threshold:  # abs(minZ[y] - maxZ[y]):
                        ptCoordZ = getMiddlePtCoord(minZ, maxZ, pt[0], x, z)
                    else:
                        pass
                        # tego else'a mozna wywalic
                        # ptCoordZ = getMiddlePtCoord(minZ, maxZ, pt[1], y, z)
                    point = [0, 0, 0]
                    point[x] = pt[0]
                    point[y] = pt[1]
                    point[z] = ptCoordZ
                    intersectPart.append(point)
                if intersectPart != []:
                    intersect.append(intersectPart)    
    return intersect


def rotateVertexByCenterPoint(vertex, center, angle):
    vertexRotated = deepcopy(vertex)
    for i in range(len(vertexRotated)):
        vertexRotated[i] = rotate2D(vertexRotated[i], center, angle)
    return vertexRotated


def moveVertex(vertex, moveX, moveY=0, moveZ=0):
    if len(vertex[0]) > 2:
        for i in range(len(vertex)):
            vertex[i][0] += moveX
            vertex[i][1] += moveY
            vertex[i][2] += moveZ
    else:
        for i in range(len(vertex)):
            vertex[i][0] += moveX
            vertex[i][1] += moveY        
    return vertex


def scaleVertex(vertex, scale):
    for i in range(len(vertex)):
        vertex[i][0] = vertex[i][0] * scale
        vertex[i][1] = vertex[i][1] * scale
    return vertex


#=====================================================================
# [[object, center], [[neighbour1, center1], [neighbour2, center2]]]
def moveGraphElement(iobject):
    objectCenter = iobject[0][1]
    xMove = -objectCenter[0]
    yMove = -objectCenter[1]
    moveVertex(iobject[0][0], xMove, yMove)
    iobject[0][1] = (0, 0)
    for nbr in iobject[1]:
        moveVertex(nbr[0], xMove, yMove)
        nbr[1] = (nbr[1][0] + xMove, nbr[1][1] + yMove)
   
#=====================================================================
# Skaluje element GraphStructure wraz z sasiadami
# [[object, center], [[neighbour1, center1], [neighbour2, center2]]]
def scaleGraphElement(iobject, scale):
    scaleVertex(iobject[0][0], scale)
    for nbr in iobject[1]:
        scaleVertex(nbr[0], scale)
        nbr[1] = (nbr[1][0] * scale, nbr[1][1] * scale)
        

#=====================================================================
# Skaluje element GraphStructure wraz z sasiadami
# [[object, center], [[neighbour1, center1], [neighbour2, center2]]]
def rotateGraphElement(iobject, angle):
    iobject[0][0] = rotateVertexByCenterPoint(iobject[0][0], [0, 0], angle)
    for nbr in iobject[1]:
        nbr[0] = rotateVertexByCenterPoint(nbr[0], [0, 0], angle)
        nbr[1] = rotate2D(nbr[1], [0, 0], angle)



if __name__ == "__main__":
    beg = [3, 3]
    end = [3, 6]
    pt = [2, 4]
    # print getAngle(beg, pt, end)

    # print getSegmentIntersection([2,2], [6,6], [3,1], [3,10])
    p1 = [140, 348]
    p2 = [96, 319]
    p3 = [94, 323]
    p4 = [77, 383]
    
    a1 = [188, 382]
    a2 = [144, 352]
    a3 = [140, 348]
    a4 = [96, 319]
    print getCrossingPoint(a1, a2, a3, a4)
    
    # print isPointInVertex([2,4.01], [[1,1],[1,4],[4,4],[4,5],[1,5],[1,8],[8,8],[8,1],[1,1]])
    # print isPointInVertex([6, 2, 0], [[1, 1, 0], [1, 3, 0], [8, 3, 0], [8, 1, 0], [1, 1, 0]])
