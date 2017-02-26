from Tools import Utils as utl, GnuplotDrawer
from copy import deepcopy
from Structures import ShapeStructure, Feature


#################################################################################################
# Class used for building 3D model of an object
#
# Overview of functionalities
# - creating 3D model based on object of Structures.ProjectionSet type
# - creating wall's features representation (Structures.Feature objects) 
#   with the sweeping algorithm
#


class ModelBuilder3D:
    
    def __init__(self, distThreshold):
        self.distThreshold = distThreshold
        self.x = 0
        self.y = 1
        self.z = 2
    
    def mirrorProjection(self, projection, maxCoordValue, coord):
        for point in projection:
            point[coord] = maxCoordValue - point[coord]
            
    
    def create3DStructure(self, projectionSet):        
        projectionSet.standardiseMainProjections()
        top = projectionSet.top
        front = projectionSet.front
        right = projectionSet.right
        
        print '------------------------'
        print right
        print top
        GnuplotDrawer.printArrowPicture([top], [[-500, 500], [-500, 500]])

        GnuplotDrawer.printArrowPicture([front], [[-500, 500], [-500, 500]])
        GnuplotDrawer.printArrowPicture([right], [[-500, 500], [-500, 500]])
                
        x = self.x
        y = self.y
        z = self.z
        
        params = {  # okreslenie wspolrzednych wyznaczajacych 
                       # szerokosc (W) i wysokosc (H) parowanych rzutow
                      'ref1_H': y, 'ref1_W': x, 'proj1_H': y, 'proj1_W': x,  # zestawienie "right" -> "front"
                      'ref2_H': x, 'ref2_W': y, 'proj2_H': y, 'proj2_W': x,  # sestawienie "right" -> "top"
                       # definicja transformacji rzutow przed wyznaczaniem scian
                       # (czasem potrzebne do wlasciwego zestawienia wzgledem siebie)
                       # elementy listy podane beda jako parametry mirrorProjection
                      'proj1_transform':[], 'proj2_transform':[],
                       # po otrzymaniu wynikowych scian trzeba zamienic wspolrzedne
                      'result1_dim_swap':[], 'result2_dim_swap':[[1, 2]],
                       # okreslenie wspolrzednych dla procedury przeciecia wynikowych scian
                       # sluza do mapowania wspolrzednych lamenej ref na finalne wspolrzedne
                       # [y, z] oznacza, ze "y" lamanej referencyjnej (ref) przeklada sie na "z" ukladu wspolrzednych w 3D
                      'const_vertex_crossing_dimension': x,
                      'variable_dim1': [y, z],
                      'variable_dim2': [x, y]
                      }
           
        wallsByRight = self.createWallsByReference(reference=right,
                                                   buildingProjection1=front,
                                                   buildingProjection2=top,
                                                   params=params)
        
        # rightWallFeatures = []
        # for feature in rightFeatures:
            # wspolrzedne x, z, y wziete na podstawie const_vertex_crossing_dimension i variable_dim[1|2]
        #    rightWallFeatures.append(self.sweepFeature(feature, y, z, x, depth=utl.getMaxPoint(front,0)[0], 
        #                                                                frontDepth=utl.getMinPoint(front,0)[0]))
                
        params = {  # okreslenie wspolrzednych wyznaczajacych 
                       # szerokosc (W) i wysokosc (H) parowanych rzutow
                      'ref1_H': y, 'ref1_W': x, 'proj1_H': y, 'proj1_W': x,  # zestawienie "front" -> "right"
                      'ref2_H': x, 'ref2_W': y, 'proj2_H': x, 'proj2_W': y,  # sestawienie "front" -> "top"
                       # definicja transformacji rzutow przed wyznaczaniem scian
                       # (czasem potrzebne do wlasciwego zestawienia wzgledem siebie)
                       # elementy listy podane beda jako parametry mirrorProjection
                      'proj1_transform':[], 'proj2_transform':['reverse'],
                       # po otrzymaniu wynikowych scian trzeba zamienic wspolrzedne
                      'result1_dim_swap':[[0, 1]], 'result2_dim_swap':[[0, 2], [1, 2]],
                       # okreslenie wspolrzednych dla procedury przeciecia wynikowych scian
                       # sluza do zmiany orientacji ukladu wspolrzednych w algorytmie
                      'const_vertex_crossing_dimension': y,
                      'variable_dim1': [x, x],
                      'variable_dim2': [y, z]
                      }
        
        wallsByFront = self.createWallsByReference(reference=front,
                                                   buildingProjection1=right,
                                                   buildingProjection2=top,
                                                   params=params)        
               
        params = {  # okreslenie wspolrzednych wyznaczajacych 
                       # szerokosc (W) i wysokosc (H) parowanych rzutow
                      'ref1_H': y, 'ref1_W': x, 'proj1_H': x, 'proj1_W': y,  # zestawienie "top" -> "right"
                      'ref2_H': x, 'ref2_W': y, 'proj2_H': x, 'proj2_W': y,  # sestawienie "top" -> "front"
                       # definicja transformacji rzutow przed wyznaczaniem scian
                       # (czasem potrzebne do wlasciwego zestawienia wzgledem siebie)
                       # elementy listy podane beda jako parametry mirrorProjection
                      'proj1_transform':[], 'proj2_transform':['reverse'],
                       # po otrzymaniu wynikowych scian trzeba zamienic wspolrzedne
                      'result1_dim_swap':[[0, 2], [0, 1]], 'result2_dim_swap':[[0, 2]],
                       # okreslenie wspolrzednych dla procedury przeciecia wynikowych scian
                       # sluza do zmiany orientacji ukladu wspolrzednych w algorytmie
                      'const_vertex_crossing_dimension': z,
                      'variable_dim1': [x, x],
                      'variable_dim2': [y, y]
                      }
        
        wallsByTop = self.createWallsByReference(reference=top,
                                                   buildingProjection1=right,
                                                   buildingProjection2=front,
                                                   params=params)
        
        projectionSet.sweepFeatures()          
        
        shapeStructure = ShapeStructure([], self.domain3D)
        shapeStructure.addWall(top, wallsByTop, None, projectionSet.topSweepedFeatures)
        for proj in projectionSet.wallsProjections:
            if proj[2] == 0:
                shapeStructure.addWall(front, wallsByFront, 0, proj[3])
            elif proj[2] == 0.5:
                shapeStructure.addWall(right, wallsByRight, 0.5, proj[3])
            else:
                shapeStructure.addWall(proj[0], [], proj[2], proj[3])
                    
        return shapeStructure
        
    
    def createWallsByReference(self, reference, buildingProjection1, buildingProjection2, params):
        # okreslenie ktore wspolrzedne rzutow opisuja wysokosc i szerokosc bryly po zlozeniu
        # s - projection, r - reference
        
        rh1 = params['ref1_H']
        rw1 = params['ref1_W']
                
        rh2 = params['ref2_H']        
        rw2 = params['ref2_W']
        
        sh1 = params['proj1_H']
        sw1 = params['proj1_W']
        
        sh2 = params['proj2_H']
        sw2 = params['proj2_W']
                            
        if params['proj1_transform'] != []:
            if params['proj1_transform'][0] == 'reverse':
                buildingProjection1.reverse()
        
        if params['proj2_transform'] != []:
            if params['proj2_transform'][0] == 'reverse':
                buildingProjection2.reverse()
        
        walls3D = []
                
        i = 0
        while i < len(reference) - 1:
            # if i != 0: # 7
            #    i += 1
            #    continue
            tmp = [reference[i], reference[i + 1]]
            
            tmp.sort(key=lambda x: x[rh1])
            refA, refB = tmp[1], tmp[0] 
            
            wallsFromProj1 = self.createWallBySingleReference(refA, refB, rh1, rw1, buildingProjection1, sh1, sw1)
            
            if len(params['result1_dim_swap']) > 0:
                for swp in params['result1_dim_swap']:
                    for wall in wallsFromProj1:          
                        for j in range(len(wall)):
                            wall[j] = [round(wall[j][0]), round(wall[j][1]), round(wall[j][2])]
                        utl.swapDimensions(wall, swp[0], swp[1])
            
            
            tmp.sort(key=lambda x: x[rh2])
            refA, refB = tmp[1], tmp[0] 
                                      
            wallsFromProj2 = self.createWallBySingleReference(refA, refB, rh2, rw2, buildingProjection2, sh2, sw2)
                  
            if len(params['result2_dim_swap']) > 0:
                for swp in params['result2_dim_swap']:
                    for wall in wallsFromProj2:      
                        for j in range(len(wall)):
                            wall[j] = [round(wall[j][0]), round(wall[j][1]), round(wall[j][2])]
                        utl.swapDimensions(wall, swp[0], swp[1])
                  
            i += 1            
          
            constDim = params['const_vertex_crossing_dimension']
            varDim1 = params['variable_dim1']
            varDim2 = params['variable_dim2']  
            
            # sprawdzanie kata nachylenia sciany 'ref' w celu wybrania optymalnego rzutu dla procedury przeciecia
            # wybor dla plaszczyzny rzutowania wspolrzednej dla ktorej rzut bedzie 'wiekszy' (czyli glebokosc odcinka refA <-> refB mniejsza)
            # if abs(refA[varDim1] - refB[varDim1]) > abs(refA[varDim2] - refB[varDim2]):
            if abs(refA[varDim1[0]] - refB[varDim1[0]]) > abs(refA[varDim2[0]] - refB[varDim2[0]]):
                cross = utl.getVertexCrossing2(wallsFromProj1, wallsFromProj2, varDim1[1], constDim, varDim2[1])
            else:
                cross = utl.getVertexCrossing2(wallsFromProj1, wallsFromProj2, varDim2[1], constDim, varDim1[1])
            
            if cross != []:
                walls3D.extend(cross)
                    
            # Odwrocenie kierunku ciagu punktow tak by od zewnatrz bryly przebiegaly zgodnie ze wsk. zegara
            '''
            TODO
            '''         
        if params['proj1_transform'] != []:
            if params['proj1_transform'][0] == 'reverse':
                buildingProjection1.reverse()
                
        if params['proj2_transform'] != []:
            if params['proj2_transform'][0] == 'reverse':
                buildingProjection2.reverse()
                
        return walls3D
    
    
    def createWallBySingleReference(self, refA, refB, rh, rw, shape, sh, sw):
        walls3D = []
        threshold = self.distThreshold
        # ref jest pozioma
        if abs(refA[rh] - refB[rh]) <= threshold:
            HH = (refA[rh] + refB[rh]) / 2.0
            
            # Dodawanie przedostatniego elementu (ale od niego potem nie zaczynamy)
            # w celu zapewnienia, ze dla j-1 bedziemy miec element
            shapeDbl = [shape[-2]] + shape
            
            crossPts = []
                        
            j = 1
            while j < len(shapeDbl) - 1:
                shapeA = shapeDbl[j]
                shapeB = shapeDbl[j + 1]
                #    a 
                #     \
                #------\------------- 
                #       \  
                #        b
                if shapeA[sh] - threshold >= HH and HH >= shapeB[sh] + threshold:
                    xCoord = utl.getMiddlePtCoord(shapeA, shapeB, HH, sh, sw)
                    crossPts.append([xCoord, -1])
                #        b 
                #       /
                #------/------------- 
                #     /  
                #    a     
                elif shapeA[sh] + threshold <= HH and HH <= shapeB[sh] - threshold:
                    xCoord = utl.getMiddlePtCoord(shapeA, shapeB, HH, sh, sw)
                    crossPts.append([xCoord, 1])
                    
                elif abs(shapeA[sh] - HH) <= threshold:
                    #       |
                    #-------a------------- 
                    #        \
                    #         b
                    if shapeDbl[j - 1][sh] - threshold >= HH and \
                       HH >= shapeB[sh] + threshold:
                        xCoord = shapeA[sw]
                        crossPts.append([xCoord, -1])
                    #
                    #------==>a------------
                    #          \
                    #           b
                    elif abs(shapeDbl[j - 1][sh] - HH) <= threshold and shapeDbl[j - 1][sw] < shapeA[sw] and \
                         HH >= shapeB[sh] + threshold:
                        xCoord = shapeA[sw]
                        crossPts.append([xCoord, -1])
                    #            /
                    #-------b<==a------------
                    #           
                    elif shapeDbl[j - 1][sh] - threshold >= HH and shapeB[sw] < shapeA[sw] and \
                         abs(shapeB[sh] - HH) <= threshold:
                        xCoord = shapeA[sw]
                        crossPts.append([xCoord, -1])
                    #       \ /
                    #--------a--------a------- nie dodajemy punktu
                    #                / \
                    elif shapeDbl[j - 1][sh] - threshold >= HH and shapeB[sh] - threshold >= HH or \
                         shapeDbl[j - 1][sh] + threshold <= HH and shapeB[sh] + threshold <= HH:
                        pass
                    else:
                        xCoord = shapeA[sw]
                        crossPts.append([xCoord, 1])  
                j += 1             
            crossPts.sort(key=lambda x: x[0])
            wallsRange = [crossPts[k] for k in range(len(crossPts)) \
                          if k == 0 or crossPts[k][1] == -1 or crossPts[k - 1][1] == -1]
            
            if len(wallsRange) > 0 and wallsRange[-1][1] == 1:
                wallsRange.reverse()
            # 1==-1==1==-1==1==-1   ==> "1" poczatek wycinka plaszczyzny, "-1" koniec wycinka 
            
            for k in range(len(wallsRange)):
                if wallsRange[k][1] == 1:
                    # mamy sciane
                    if len(wallsRange) > k + 1 and wallsRange[k + 1][1] == -1:
                        xCoordA = wallsRange[k][0]
                        xCoordB = wallsRange[k + 1][0]
                        wall3D = [[xCoordA, refA[rw], HH], [xCoordA, refB[rw], HH],
                                  [xCoordB, refB[rw], HH], [xCoordB, refA[rw], HH], [xCoordA, refA[rw], HH]]
                    # mamy odcinek, ktory bedziemy interpretowac jako sciane o powierzchni 0
                    else:
                        xCoordA = wallsRange[k][0]
                        wall3D = [[xCoordA, refA[rw], HH], [xCoordA, refB[rw], HH], [xCoordA, refA[rw], HH]]
                    
                    walls3D.append(wall3D)
                
        else:
            j = 0
            wall3D = []
            while j < len(shape) - 1:
                shapeA = shape[j]
                shapeB = shape[j + 1]
                # poczatek krawedzi miesci sie w granicach
                if shapeA[sh] <= refA[rh] + threshold and \
                   shapeA[sh] >= refB[rh] - threshold:
                    yCoordA = zCoordB = xCoordB = None
                    # jezeli poczatek shape jest w otoczeniu ktoregos konca ref                    
                    if abs(shapeA[sh] - refA[rh]) <= threshold:
                        yCoordA = refA[rw]
                        # sprawdzamy czy drugi koniec shape nie wychodzi poza ref
                        if shapeB[sh] < refB[rh] - threshold:
                            # trzeba wyliczyc x w plaszczyznie shape
                            xCoordB = utl.getMiddlePtCoord(shapeA, shapeB, refB[rh], sh, sw)
                            yCoordB = refB[rw]
                            zCoordB = refB[rh]
                    elif abs(shapeA[sh] - refB[rh]) <= threshold:
                        yCoordA = refB[rw]
                        # sprawdzamy czy drugi koniec shape nie wychodzi poza ref
                        if shapeB[sh] > refA[rh] + threshold:
                            xCoordB = utl.getMiddlePtCoord(shapeA, shapeB, refA[rh], sh, sw)
                            yCoordB = refA[rw]
                            zCoordB = refA[rh]
                    else:
                        yCoordA = utl.getMiddlePtCoord(refA, refB, shapeA[sh], rh, rw)
                        # drugi punkt dodajemy tylko jezeli linia wychodzi poza ref
                        # w przeciwnym wypadku nie dodajemy, bo zostanie oddany przy wyliczeniu dla kolejnej linii shape
                        if shapeB[sh] > refA[rh] + threshold:
                            # trzeba wyliczyc x w plaszczyznie front
                            xCoordB = utl.getMiddlePtCoord(shapeA, shapeB, refA[rh], sh, sw)
                            yCoordB = refA[rw]
                            zCoordB = refA[rh]
                        elif shapeB[sh] < refB[rh] - threshold:
                            xCoordB = utl.getMiddlePtCoord(shapeA, shapeB, refB[rh], sh, sw)
                            yCoordB = refB[rw]
                            zCoordB = refB[rh]

                    wall3D.append([shapeA[sw], yCoordA, shapeA[sh]])
                    if zCoordB is not None:
                        wall3D.append([xCoordB, yCoordB, zCoordB])
                    # to chyba niepotrzebne 26.05.13
                    # if zCoordA2 is not None:
                    #    wall3D.append([shapeA[sw], shapeA[sh], zCoordA2])
                        
                # krawedz shape wychodzi poza krawedz ref w obie strony (shapeA jest wyzej)
                elif shapeA[sh] > refA[rh] + threshold and \
                     shapeB[sh] < refB[rh] - threshold:
                    xCoordA = utl.getMiddlePtCoord(shapeA, shapeB, refA[rh], sh, sw)
                    yCoordA = refA[rw]
                    zCoordA = refA[rh]
                    xCoordB = utl.getMiddlePtCoord(shapeA, shapeB, refB[rh], sh, sw)
                    yCoordB = refB[rw]
                    zCoordB = refB[rh]
                    wall3D.append([xCoordA, yCoordA, zCoordA])
                    wall3D.append([xCoordB, yCoordB, zCoordB])                    
                # krawedz shape wychodzi poza krawedz ref w obie strony (shapeB jest wyzej)
                elif shapeB[sh] > refA[rh] + threshold and \
                     shapeA[sh] < refB[rh] - threshold: 
                    xCoordB = utl.getMiddlePtCoord(shapeA, shapeB, refA[rh], sh, sw)
                    yCoordB = refA[rw]
                    zCoordB = refA[rh]
                    xCoordA = utl.getMiddlePtCoord(shapeA, shapeB, refB[rh], sh, sw)
                    yCoordA = refB[rw]
                    zCoordA = refB[rh]
                    wall3D.append([xCoordA, yCoordA, zCoordA])
                    wall3D.append([xCoordB, yCoordB, zCoordB])
                # koniec krawedzi miesci sie wewnatrz zakresu wyznaczonego przez ref (poczatek jest poza [pierszy if])
                # ale ref nie jest pozioma (ten przypadek rowniez w pierwszym if-ie)
                elif abs(refA[rh] - refB[rh]) > threshold:                        
                    if shapeA[sh] > refA[rh] and \
                       shapeB[sh] < refA[rh] - threshold:
                        xCoordA = utl.getMiddlePtCoord(shapeA, shapeB, refA[rh], sh, sw)
                        yCoordA = refA[rw]
                        zCoordA = refA[rh]
                        wall3D.append([xCoordA, yCoordA, zCoordA])
                    elif shapeA[sh] < refB[rh] and \
                         shapeB[sh] > refB[rh] + threshold:
                        xCoordA = utl.getMiddlePtCoord(shapeA, shapeB, refB[rh], sh, sw)
                        yCoordA = refB[rw]
                        zCoordA = refB[rh]
                        wall3D.append([xCoordA, yCoordA, zCoordA])                
                j += 1
            # domkniecie sciany
            if len(wall3D) > 0:
                begin = deepcopy(wall3D[0])
                wall3D.append(begin)
                walls3D.append(wall3D)
       
        return walls3D

    
#############################################################################################
# ustala glebokosc atrybutu sciany
# @depth - okrsla glebokosc (-1 - otwor na wylot)
#
def sweepFeature(feature, x, y, coordDepth, backDepth=-1, frontDepth=0):
    # zmiana orientacji atrybutu (feature) w przestrzeni
    featureXY = []
    for point in feature:
        pointXY = [0, 0, 0]
        pointXY[x] = point[0]
        pointXY[y] = point[1]
        featureXY.append(pointXY)
    sweepWalls = []
    for i in range(len(featureXY) - 1):
        pt = featureXY[i]
        pt2 = featureXY[i + 1]    
        wall = []
        pt[coordDepth] = frontDepth
        pt2[coordDepth] = frontDepth
        wall.append(deepcopy(pt))
        wall.append(deepcopy(pt2))
        pt2[coordDepth] = backDepth
        wall.append(deepcopy(pt2))
        pt[coordDepth] = backDepth
        wall.append(deepcopy(pt))
        pt[coordDepth] = frontDepth
        wall.append(deepcopy(pt))
        sweepWalls.append(wall)
    fullFeature = Feature(featureXY, sweepWalls)
    return fullFeature
        
                    
