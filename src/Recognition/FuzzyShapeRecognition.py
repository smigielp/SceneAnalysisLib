
from Tools import Utils, GnuplotDrawer
from copy import deepcopy
from time import sleep
import math

ANGLE_STEP = 5

def getObjectBorderSpectrum(vectorObject, angleStep=ANGLE_STEP):
    spectrumDict = {}
    i = 0
    while i < 360:
        spectrumDict[i] = []
        i = i + angleStep
    print "===========", vectorObject
    centroid = Utils.getCentroid(vectorObject)
    
    #print spectrumDict
    #print centroid
    for i in range(len(vectorObject)-1):
        begin = deepcopy(vectorObject[i])
        end   = deepcopy(vectorObject[i+1])
        
        # calculating angles from centroid (center of vectorObject) to beginning and end of line
        angleBegin = 360 - Utils.getLineAngle(centroid, begin) * 180
        angleEnd   = 360 - Utils.getLineAngle(centroid, end) * 180
       
        # if examined line crosses straight line going from centroid in right direction
        # the angles range has to be split to maintain sequence as it overlaps 360 degree circle
        crossing360Degree = Utils.getCrossingPoint(begin, end, centroid, [10000, centroid[1]], checkSegmentCrossing=True)
        if crossing360Degree is not None and crossing360Degree[2] == True:
            # first point has to be before second (when going clockwise)
            if angleEnd > angleBegin:
                tmp = angleBegin
                angleBegin = angleEnd
                angleEnd = tmp
            # setting range for spectrum calculation for single line
            spectrumBegin = int((angleBegin + angleStep) / angleStep) * angleStep
            spectrumEnd   = int(angleEnd / angleStep) * angleStep
            
            scanRange = []
            j = spectrumBegin
            while j < 360:
                scanRange.append(j)
                j = j + angleStep
            j = 0
            while j <= spectrumEnd:
                scanRange.append(j)
                j = j + angleStep 
        else:
            # first point has to be before second (when going clockwise)
            if angleBegin > angleEnd:
                tmp = angleBegin
                angleBegin = angleEnd
                angleEnd = tmp
            # setting range for spectrum calculation for single line
            spectrumBegin = int((angleBegin + angleStep) / angleStep) * angleStep
            spectrumEnd   = int(angleEnd / angleStep) * angleStep
            
            scanRange = []
            j = spectrumBegin
            while j <= spectrumEnd:
                scanRange.append(j)
                j = j + angleStep
                
        #print scanRange
        # calculating distance from centroid to examined line on subsequent angles from scanRange
        for rayAngle in scanRange:
            # creating straight line from centroid with subsequent angle
            ray = [centroid, Utils.rotate2D([10000, centroid[1]], centroid, -rayAngle/180.0)]
            #print ray
            crossingPoint = Utils.getCrossingPoint(begin, end, ray[0], ray[1])
            crossingPoint[0] = round(crossingPoint[0], 2)
            crossingPoint[1] = round(crossingPoint[1], 2)
            spectrumDict[rayAngle].append(Utils.getDistance(centroid, crossingPoint))
            
    # transform spectrum dict into list
    spectrumList = []
    for key, value in spectrumDict.iteritems():
        spectrumList.append([key, value])
    return sorted(spectrumList, key=lambda values: values[0]) 
            
        

########################################################################################
# Function checks if two representations given in distances from centroid to walls
# describe similar shapes
def comparePatterns(pattern1, pattern2, angleStep=ANGLE_STEP): 
    if len(pattern1) != len(pattern2):
        print "Error: inconsistent patterns - different ray count"
        return None
    pattern1 = pattern1 + pattern1     
    print "=================="
    print pattern1
    print pattern2
    for i in range(len(pattern1) / 2):
        rayProportions = []
        for j in range(len(pattern2)):
            if len(pattern2[j][1]) == 0 or pattern2[j][1][0] == 0:
                rayProportions.append(0)     
            else:
                if len(pattern1[i + j][1]) == 0:
                    ray1 = 0.0
                else:
                    ray1 = float(pattern1[i + j][1][0])
                rayProportions.append(ray1 / float(pattern2[j][1][0]))
        meanProportion = sum(rayProportions) / len(rayProportions)
        standardDev = 0
        for j in range(len(rayProportions)):
            standardDev += (rayProportions[j] - meanProportion) ** 2
        standardDev = math.sqrt(standardDev / len(rayProportions))      
        # sprawdzenie czy roznice miedzy proporcjami dlugosci scian
        # porownywanych bryl sa dostatecznie male 
        if standardDev < meanProportion * 0.15:  
            # print dirChange1
            # print dirChange2
            return {'scale': rayProportions[0], 'rotate': (pattern1[i][0] - pattern2[0][0]) * angleStep}   
    return None
    
    
def findSinglePattern(vectorObject, vectorObjectList):
    spectrum1 = getObjectBorderSpectrum(vectorObject)
    for idx, object in enumerate(vectorObjectList):
        spectrum2 = getObjectBorderSpectrum(object)
        found = comparePatterns(spectrum1, spectrum2)
        if found is not None:
            return [idx, found]
    return None
    
    
'''
pAngleStep = 5    
    
polygon1 = [[-2, -2], [-2, 2], [2, 2], [2, -2], [-2, -2]]
polygon2 = [[-3, -3], [-3, 3], [3, 3], [3, -3], [-3, -3]]
spectrum1 = getObjectBorderSpectrum(polygon1, angleStep=pAngleStep)
spectrum2 = getObjectBorderSpectrum(polygon2, angleStep=pAngleStep)

#polygon3 = [[260.0, 80.0], [206, 80], [199, 69], [34, 69], [33, 71], [33, 96], [32, 98], [34, 146], [107, 145], [110, 184], [163, 184], [173, 182], [173, 146], [202, 145], [204, 123], [262, 121], [260.0, 80.0]]
#spectrum3 = getObjectBorderSpectrum(polygon3, angleStep=pAngleStep)
#GnuplotDrawer.printPolygonCentroidSpectrum(spectrum3)

polygon4 = [[98.5, 258.0], [147, 202], [179, 226], [220, 180], [193, 151], [213, 126], [197, 110], [236, 66], [203, 37], [166, 79], [156, 74], [38, 205], [98.5, 258.0]]
spectrum4 = getObjectBorderSpectrum(polygon4, angleStep=pAngleStep)
GnuplotDrawer.printPolygonCentroidSpectrum(spectrum4 + spectrum4)


#result = comparePatterns(spectrum3, spectrum4, pAngleStep) 
#print result   
sleep(100)
'''        
        