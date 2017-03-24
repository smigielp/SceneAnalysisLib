
from Tools import Utils
from copy import deepcopy


def getObjectBorderSpectrum(vectorObject, angleDensity=10):
    spectrumDict = {}
    i = 0
    while i < 360:
        spectrumDict[i] = []
        i = i + angleDensity
    centroid = Utils.getCentroid(vectorObject)
    
    print spectrumDict
    print centroid
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
            spectrumBegin = int((angleBegin + angleDensity) / angleDensity) * angleDensity
            spectrumEnd   = int(angleEnd / angleDensity) * angleDensity
            
            scanRange = []
            j = spectrumBegin
            while j < 360:
                scanRange.append(j)
                j = j + angleDensity
            j = 0
            while j <= spectrumEnd:
                scanRange.append(j)
                j = j + angleDensity 
        else:
            # first point has to be before second (when going clockwise)
            if angleBegin > angleEnd:
                tmp = angleBegin
                angleBegin = angleEnd
                angleEnd = tmp
            # setting range for spectrum calculation for single line
            spectrumBegin = int((angleBegin + angleDensity) / angleDensity) * angleDensity
            spectrumEnd   = int(angleEnd / angleDensity) * angleDensity
            
            scanRange = []
            j = spectrumBegin
            while j <= spectrumEnd:
                scanRange.append(j)
                j = j + angleDensity
                
        print scanRange
        # calculating distance from centroid to examined line on subsequent angles from scanRange
        for rayAngle in scanRange:
            # creating straight line from centroid with subsequent angle
            ray = [centroid, Utils.rotate2D([10000, centroid[1]], centroid, -rayAngle/180.0)]
            print ray
            crossingPoint = Utils.getCrossingPoint(begin, end, ray[0], ray[1])
            crossingPoint[0] = round(crossingPoint[0], 2)
            crossingPoint[1] = round(crossingPoint[1], 2)
            spectrumDict[rayAngle].append(Utils.getDistance(centroid, crossingPoint))
            
    # transform spectrum dict into list
    spectrumList = []
    for key, value in spectrumDict.iteritems():
        spectrumList.append([key, value])
    return sorted(spectrumList, key=lambda values: values[0]) 
            
        
        
        
        