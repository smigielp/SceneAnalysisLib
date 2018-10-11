
from copy import deepcopy
from Tools import Utils
from Tools import GnuplotDrawer
import math


###########################################################################################
# This file collects the set of methods used for objects recognition
#
# Overview of functionalities 
# - extracting pattern by turning vector sequence into sequence of angles and primitives 
# - comparing two patterns 
# - searching single pattern in the pattern list
# - searching set of patterns in the pattern list
# - searching set of patterns with spatial relations between object in the pattern list 
# - comparing objects shapes by checking overlapping corners
# - searching the object with spatial context (nearby objects) in the graph representation of the scene
#


'''
angleTranslate = [[1.876, 2, 0],
                [0, 0.125, 0],
                [0.126, 0.375, 1],
                [0.376, 0.625, 2],
                [0.626, 0.875, 3],
                [0.876, 1.125, 4],
                [1.126, 1.375, 5],
                [1.376, 1.625, 6],
                [1.626, 1.875, 7]]

def getPrimitive(angle):
    for trans in angleTranslate:
        if angle >= trans[0] and angle <= trans[1]:
            return trans[2]
    return -1000
'''

def compareAngles(angle1, angle2):
    threshold = 0.2
    angleDiff = (angle1 - angle2) % 2
    return angleDiff < threshold or angleDiff > 2.0 - threshold  


########################################################################################            
# Tworzy reprezentacje bryly na podstawie wektorow 
# stanowiacych obrys zewnetrzny
# Reprezentacja jest postaci [[dir1, count1], [dir2, count2], ... ]
# gdzie dir - kierunek wektorow czastkowych, count - liczba wektorow w danym kierunku
# kazda taka para koduje jedna sciane bryly  
def extractPattern(vertex, basePatternLen):
    pattern = []
    print '==============='
    print vertex
    for i in range(len(vertex) - 1):
        line = [vertex[i], vertex[i + 1]]
        lLen = Utils.getDistance(line[0], line[1])
        primitiveCount = (lLen / basePatternLen)
        if line[0] == line[1]:
            continue
        angle = round(Utils.getLineAngle(line[0], line[1]), 3)        
        pattern.append([angle, primitiveCount])        
    return pattern
        

########################################################################################
# Funkcja sprawdza czy dwie reprezentacje bryl przedstawiaja ten sam obiekt
# niezaleznie od roznicy skali oraz obrotu
def comparePatterns(pat1, pat2):
    # sprawdzenie czy roznia sie iloscia scian
    if len(pat1) != len(pat2):
        print 'roznica ilosci scian (', len(pat1), ', ', len(pat2), ')'
        return None    
    # print 'ilosc scian pasuje (', len(pat1), ')'    
    # zapisanie informacji o zmianie kierunku wektorow czastkowych (scian bryly)
    # oraz dlugosci sciany poprzedzajacej zmiane kierunku
    dirChange1 = []
    dirChange2 = []
    # STARE mod pomniejszone o 1, bo przedzial dla '0' jest podzielony na dwa
    # STARE mod = len(angleTranslate) - 1
    mod = 2
    for i in range(len(pat1) - 1):
        dirChange1.append([ (pat1[i + 1][0] - pat1[i][0]) % mod, pat1[i][1] ])
        dirChange2.append([ (pat2[i + 1][0] - pat2[i][0]) % mod, pat2[i][1] ])
    dirChange1.append([ (pat1[0][0] - pat1[-1][0]) % mod, pat1[-1][1] ])    
    dirChange2.append([ (pat2[0][0] - pat2[-1][0]) % mod, pat2[-1][1] ])
    # print pat1
    # print pat2      
    dirChange1 = dirChange1 + dirChange1
    # wyszukanie podciagu directionChange2 w podwojonym directionChange1
    # zapisanie proporcji dlugosci scian porownywanych bryl
    # sprawdzenie czy bryly naleza do tej samej klasy                 
    for i in range(len(dirChange1) / 2):
        j = 0
        while j < len(dirChange2) and compareAngles(dirChange1[i + j][0], dirChange2[j][0]):
            j += 1
        if j == len(dirChange2):
            # przechowuje proporcje dlugosci scian dopasowanych ciagow
            wallLenProps = []
            for k in range(len(dirChange2)):
                wallLenProps.append(float(dirChange1[i + k][1]) / float(dirChange2[k][1]))
            # sprawdzenie dopasowania dlugosci scian
            # jak dopasowanie nie wystarcza szukamy nowego dopasowania podciagu
            meanProp = sum(wallLenProps) / len(wallLenProps)
            standardDev = 0
            for k in range(len(wallLenProps)):
                standardDev += (wallLenProps[k] - meanProp) ** 2
            standardDev = math.sqrt(standardDev / len(wallLenProps))      
            # sprawdzenie czy roznice miedzy proporcjami dlugosci scian
            # porownywanych bryl sa dostatecznie male 
            if standardDev < meanProp * 0.15:  
                # print dirChange1
                # print dirChange2   
                return {'scale': wallLenProps[0], 'rotate': (pat1[i][0] - pat2[0][0]) % 2}   
    return None
    
    
########################################################################################
# Function realizing complete task of pattern recognition
# patrenElement - vector representation of object dedicated to be searched
# patternList   - list of vector representations in which patternElement is searched
# primitiveLen  - length of walls used in object representation build method
#  
def findSinglePattern(patternElement, patternList, primitiveLen=5):
    fullPattern = []
    for v in patternList:
        pattern = extractPattern(v, primitiveLen)
        fullPattern.append(pattern) 
        print pattern
          
    singlePattern = extractPattern(patternElement, primitiveLen)        
    print singlePattern
    
    for idx, pattern in enumerate(fullPattern):
        diffParams = comparePatterns(pattern, singlePattern) 
        if diffParams is not None :      
            return [idx, diffParams]
    return None
       
     
def extractAllPatterns(objectList, primitiveLen):
    objPatternList = []
    for tmp in objectList:
        pattern = extractPattern(tmp, primitiveLen)
        objPatternList.append([tmp, pattern])
    return objPatternList
    
    
########################################################################################
# funkcja zwraca listy zawierajace obiekty wzorcowe oraz
# listy odpowiadajacych im obiektow z drugiej listy
#  ([
#    {obj1, pat1}, 
#    {obj2, pat2}
#   ],
#   [ 
#       [{obj1, objIdx1, pat1, scale1, rotate1}, {obj1, objIdx1, pat1, scale1, rotate1}], 
#       [{obj2, objIdx2, pat2, scale2, rotate2}]] 
#   ])
#--------------------------------
def findAllPatterns(smallPatternList, fullPatternList):
    basicPatternList = []
    completePatternList = []
    for smallObject, smallPattern in smallPatternList:
        basicPatternList.append({"obj":smallObject,
                                 "pat":smallPattern})
        patternMatchingList = []
        for idx, objectPattern in enumerate(fullPatternList):
            baseObject = objectPattern[0]
            pattern = objectPattern[1]
            diffParams = comparePatterns(smallPattern, pattern)
            if diffParams is not None:
                patternMatchingList.append({"obj": baseObject,
                                        "objIdx": idx,
                                       "pat": pattern,
                                       "scale": diffParams["scale"],
                                       "rotate": diffParams["rotate"]})
        completePatternList.append(patternMatchingList)
    return (basicPatternList, completePatternList)      
                

########################################################################################
# Searching group of objects with their spatial relations 
#
def findComplexPattern(smallPatternList, fullPatternList, primitiveLen):
    distThreshold = 30.0
    scaleThreshold = 0.2
    rotationThreshold = 0.1
    
    prevMainAngle = -1
    prevMatchingAngle = -1
    
    lst = findAllPatterns(smallPatternList, fullPatternList, primitiveLen)
    # lista obiektow do rozpoznania
    smallList = lst[0]  
    
    # struktura przechowujaca zestawy dopasowanych pojedynczo budynkow
    fullStruct = lst[1]
    
    matchingList = []
    baseMainObj = smallList[0]
    baseMainObjCenter = Utils.getWeightCenter(baseMainObj['obj'])
    
    print fullStruct
    for B0 in fullStruct[0]:        
        s = B0['scale']
        r = B0['rotate']
        print 'Base scale/rotate - ', s, '/', r
        matchingList = [B0]
        matchingMainObjCenter = Utils.getWeightCenter(B0['obj'])
        for idx, List in enumerate(fullStruct[1:]):
            # Proba znalezienia kolejnego obiektu (na kolejnej liscie)
            print '    dobieramy kolejnego ' 
            i = idx + 1
            # Obliczenie odleglosci obiektow, do ktorych dopasowujemy
            baseTmpObjCenter = Utils.getWeightCenter(smallList[i]['obj'])
            baseDist = Utils.getDistance(baseMainObjCenter, baseTmpObjCenter)
            for j, B in enumerate(List):
                tmpScale = B['scale']
                tmpRotate = B['rotate']
                print '     Tmp scale/rotate - ', tmpScale, '/', tmpRotate
                
                matchingTmpObjCenter = Utils.getWeightCenter(B['obj'])
                matchingDist = Utils.getDistance(matchingTmpObjCenter, matchingMainObjCenter)
                print '     baseDist, matchingDist, scaled matchingDist: ', baseDist, matchingDist, (s * matchingDist)
                
                # Porownanie skali obrotu i odleglosci obiektu bazowego (z pierwszej listy)
                # z aktulanie parametrami aktualnie przetwarzanego
                if scaleThreshold >= abs(tmpScale - s) \
                    and rotationThreshold >= abs(tmpRotate - r) \
                    and distThreshold >= abs(s * matchingDist - baseDist):                    
                    
                    mainAngle = round(Utils.getLineAngle(baseMainObjCenter, baseTmpObjCenter), 3)
                    matchingAngle = round(Utils.getLineAngle(matchingMainObjCenter, matchingTmpObjCenter), 3)
                    # STARE mainPrimitive = getPrimitive(mainAngle)
                    # STARE matchingPrimitive = getPrimitive(matchingAngle)
                    # print 'Primitives main/matching: ', (prevMainPrimitive - mainPrimitive), (prevMatchingPrimitive - matchingPrimitive)
                    # print 'Primitives main/matching: ', (mainPrimitive), (matchingPrimitive)
                    if prevMainAngle < 0 and prevMatchingAngle < 0 or \
                        compareAngles((prevMainAngle - mainAngle) % 2, (prevMatchingAngle - matchingAngle) % 2):
                        # Mamy kolejny pasujacy obiekt 
                        # przechodziny do nastepnej listy
                        print '    === matching building found ==='
                        prevMainAngle = mainAngle
                        prevMatchingAngle = matchingAngle
                        matchingList.append(B)
                        break
                if j == len(List) - 1:
                    print "Matching FAILED"
                    return []
            if len(matchingList) == len(smallList):
                print "Matching OK"
                return matchingList
    return []

