from copy import deepcopy
from Tools import Utils
from Tools import GnuplotDrawer
import FuzzyShapeRecognition


#########################################################################################
# Porownuje w sposob rozmyty podobne obiekty 
# znajdujace sie w jednym obszarze
def fuzzyCompareObjects(vertex1, vertex2, distThreshold):
    sumDist = 0
    for pt1 in vertex1:
        minDist = 100000
        for idx in range(len(vertex2) - 1):
            dist = Utils.getPointToSegmentDist(vertex2[idx], vertex2[idx + 1], pt1)
            if minDist > dist:
                minDist = dist
        sumDist += minDist
    meanDist = sumDist / len(vertex1)
    if meanDist < distThreshold:
        return meanDist
    else:
        return meanDist
        

#########################################################################################
# Wyszukuje obiekt w grafie. Jezeli podany obiekt zawiera sasiadow
# sprawdzane jest dopasowanie wraz z sasiadami
# parametry:
#    lookupObjectIn - szukany obiekt wraz z ewentualnymi sasiadami
#    lookupGraphIn  - graf przechowujacy obiekty sceny
def findPatternInGraph(lookupObjectIn, lookupGraphIn):    
    # lookupObject: 
    # [[object, center], [[neighbour1, center1], [neighbour2, center2]]]
    # lookupGraph:
    # [ [[object1, center1], [[neighbour1, center1], [neighbour2, center2]]]
    #  [[object2, center2], [[neighbour1, center1], [neighbour2, center2]]] ]
    distThreshold = 20  # TODO: to mozna wyliczyc jako ulamek sredniej odleglosci
    
    lookupObject = deepcopy(lookupObjectIn)
    lookupGraph = deepcopy(lookupGraphIn)
    
    lookupPattern = FuzzyShapeRecognition.getObjectBorderSpectrum(lookupObject[0][0])      
        
    searchResults = []
    for lkpIdx, graphObject in enumerate(lookupGraph):
        graphObjPattern = FuzzyShapeRecognition.getObjectBorderSpectrum(graphObject[0][0])  
        diffParams = FuzzyShapeRecognition.comparePatterns(lookupPattern, graphObjPattern) 
        if diffParams is not None :  
            # znalezione dopasowanie wyszukiwanego elementu     
            # konstruujemy strukture do przechowywania dopasowanych obiektow
            # [ {foundObj, foundObjCenter, indexInGraph}, [
            #
            #         
            matchedObject = {'obj':      graphObject[0][0],
                             'center':   graphObject[0][1],
                             'graphIdx': lkpIdx,
                             'scale':    diffParams['scale'],
                             'rotate':   diffParams['rotate'] }
            
            scale = diffParams['scale']
            rotate = diffParams['rotate']
            
            # przeniesienie lookupObject do 0,0
            Utils.moveGraphElement(lookupObject)
            
            Utils.moveGraphElement(graphObject)
            Utils.rotateGraphElement(graphObject, -rotate/180.0)
            Utils.scaleGraphElement(graphObject, scale)
            
            # GnuplotDrawer.printObjectGraphElement([lookupObject, graphObject], [[-200,350],[-280,200]])
            GnuplotDrawer.printObjectGraphElement([lookupObject, graphObject]) #, [[-300, 300], [-100, 500]])
            
            matchCount = 0
            matchedIndexes = []
            matchingResults = []
            
            for lookupObjectNbr in lookupObject[1]:
                lkpNbrCenter = lookupObjectNbr[1]
                found = False
                for idx, graphObjectNbr in enumerate(graphObject[1]):
                    graphObjNbrCenter = graphObjectNbr[1]
                    if Utils.getDistance(lkpNbrCenter, graphObjNbrCenter) < distThreshold:
                        # mamy kandydata na match
                        result = fuzzyCompareObjects(lookupObjectNbr[0], graphObjectNbr[0], distThreshold)
                        if result < distThreshold:
                            found = True
                            matchCount += 1
                            matchedIndexes.append(idx)
                if found:
                    matchingResults.append(result)
                else:
                    matchingResults.append(-1)
            # TODO: dodac do wyliczen stopien zgodnosci glownego obiektu
            matchRate = matchCount 
            
            searchResults.append( 
                    {'matchRate': matchRate,
                    'matched'  : {lkpIdx: matchedIndexes},
                    'fullStats': {'centeObjMatchStats' : matchedObject,
                                  'neighborMatchStats': matchingResults}
                    })
    # sorting match by matchRate, keeping best match first
    return sorted(searchResults, key=lambda values: -values['matchRate'])      
    

