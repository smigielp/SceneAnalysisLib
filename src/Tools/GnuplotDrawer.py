import os

import Gnuplot


############################################################################################
# Printing 2D and 3D objects in Gnuplot diagrams
#


gnuPlots = []  
domain3D = None  

gp = Gnuplot.Gnuplot(persist=0)

def addPoints(graph, points):
    """
    :param graph:   graph on which arrow will be drawn
    :param points:  arrays of point to be drawn
    Adds points to the graph and redraw everything
    """
    plots = []
    for point in points:
        plots.append(Gnuplot.PlotItems.Data(point))
    graph.replot(*plots)

def setPoints(graph, points, is2D = False):
    """
    :param graph:   graph on which arrow will be drawn
    :param points:  arrays of point to be drawn
    :param is2D:    whether graph should be 2d or 3d
    Draws points on the graph. This function is plotting the graph.
    """
    plots = []
    for pointsArray in points:
        plots.append(Gnuplot.PlotItems.Data(pointsArray))
    if is2D:
        graph.plot(*plots)
    else:
        graph.splot(*plots)


def setArrow(graph, arrow, id=1):
    """
    :param graph:   graph on which arrow will be drawn
    :param arrow:   array of 2 coordinates (start and end of the arrow)
    :param id:      identifier (integer) of arrow to be modified/created
    Draws arrow on graph
    !! has to be called before plotting !!
    """
    graph('set arrow %i from %s,%s,%s to %s,%s,%s' % (id,
                                                    arrow[0][0], arrow[0][1], arrow[0][2],
                                                    arrow[1][0], arrow[1][1], arrow[1][2]))


def setLabel(graph, pos, label, id=1):
    """
    :param graph:   graph on which label will be drawn
    :param pos:     position in 3d space of this label
    :param label:   string to display
    :param id:      identifier (integer) of label to be modified/created
    Draws label on graph
    !! has to be called before plotting !!
    """
    graph('set label %i "%s" at %s,%s,%s' % (id,
                                             label,
                                             pos[0], pos[1], pos[2]))


def printMultiPointPicture(mapToPrint, domain):
    #gp = Gnuplot.Gnuplot(persist=0)
    gp('set xrange [' + str(domain[0][0] - 1) + ':' + str(domain[0][1] + 1) + ']')
    gp('set yrange [' + str(domain[1][0] - 1) + ':' + str(domain[1][1] + 1) + ']')
    if len(domain) > 2:
        gp('set zrange [' + str(domain[2][0] - 1) + ':' + str(domain[2][1] + 1) + ']')
    plots = []
    for pointList in mapToPrint:  
        plots.append(Gnuplot.PlotItems.Data(pointList))
    if len(domain) > 2:
        gp.splot(*plots)
    else:
        gp.plot(*plots)
    gnuPlots.append(gp)
    return gp
   
        
def printVectorPicture(mapToPrint, domain):
    # type: (object, object) -> object
    gp = Gnuplot.Gnuplot(persist=0) 
                      
    gp('set xrange [' + str(domain[0][0] - 1) + ':' + str(domain[0][1] + 1) + ']')
    gp('set yrange [' + str(domain[1][0] - 1) + ':' + str(domain[1][1] + 1) + ']')
    
    plots = []
    for key in mapToPrint:            
        plots.append(Gnuplot.PlotItems.Data(key, with_='lines'))
    if len(domain) > 2:
        gp('set ztics 100')
        gp('set zrange [' + str(domain[2][0] - 1) + ':' + str(domain[2][1] + 1) + ']')
        gp.splot(*plots)
    else:
        gp.plot(*plots)   
    gnuPlots.append(gp)
    return gp

def saveToFile(gnuPlot, name,imgSize = (400,300),path="debug/vecs/"):
    if not os.path.exists(path):
        os.makedirs(path)
    gnuPlot("set terminal png size "+str(imgSize[0])+","+str(imgSize[1])+" enhanced font \"Helvetica,12\"")
    gnuPlot("set output '"+path+name+".png'")
    gnuPlot("replot")
    gnuPlot("set term win")

def printArrowPicture(mapToPrint, domain=None):   
    gp = Gnuplot.Gnuplot(persist=0) 
    
    if domain is not None:                  
        gp('set xrange [' + str(domain[0][0] - 1) + ':' + str(domain[0][1] + 1) + ']')
        gp('set yrange [' + str(domain[1][0] - 1) + ':' + str(domain[1][1] + 1) + ']')
        if len(domain) > 2:
            gp('set zrange [' + str(domain[2][0] - 1) + ':' + str(domain[2][1] + 1) + ']')
                      
    # for obj in mapToPrint:
    #    for wall in obj:    
    for wall in mapToPrint:
        for i in range(len(wall) - 1):
            if len(domain) == 2:
                gp('set arrow from %s,%s to %s,%s' % (wall[i][0], wall[i][1], wall[i + 1][0], wall[i + 1][1]))
            elif len(domain) == 3:
                gp('set arrow from %s,%s,%s to %s,%s,%s' % (wall[i][0], wall[i][1], wall[i][2], wall[i + 1][0], wall[i + 1][1], wall[i + 1][2])) 

    # musi byc zeby gnuplot w ogole otworzyl okno
    if len(domain) == 2:
        plots = [Gnuplot.PlotItems.Data([0, 0], with_='lines')]
        gp.plot(*plots)
    elif len(domain) == 3:
        plots = [Gnuplot.PlotItems.Data([0, 0, 0], with_='lines')]
        gp.splot(*plots)
    gnuPlots.append(gp)
    return gp


###################################################################
# objectsToMark: { idx1: [neighborIdx1, neighborIdx2], 
#                  idx2: [neighborIdx1] }
def printObjectGraph(graph, objectsToMark=None):
    graphToPrint = graph.getGraph()
    domain = graph.getDomain()
    
    gp = Gnuplot.Gnuplot(persist=0) 
                      
    gp('set xrange [' + str(domain[0][0] - 1) + ':' + str(domain[0][1] + 1) + ']')
    gp('set yrange [' + str(domain[1][0] - 1) + ':' + str(domain[1][1] + 1) + ']')
    
    gp('set style arrow 1 head filled size screen 0.03,10,30 lw 3')
    gp('set style arrow 2 head filled size screen 0.03,15,45 ls 1')
    
    plots = []
    for idx, eobject in enumerate(graphToPrint):            
        if objectsToMark is not None and idx in objectsToMark:
            plots.append(Gnuplot.PlotItems.Data(eobject[0][0], with_='lines lw 3'))
            for nbrIdx, reference in enumerate(eobject[1]):
                if objectsToMark[idx] == 'all' or nbrIdx in objectsToMark[idx]: 
                    gp('set arrow arrowstyle 1 from %s,%s to %s,%s' % (eobject[0][1][0], eobject[0][1][1], reference[1][0], reference[1][1]))
                else:
                    gp('set arrow from %s,%s to %s,%s' % (eobject[0][1][0], eobject[0][1][1], reference[1][0], reference[1][1]))
        else:
            plots.append(Gnuplot.PlotItems.Data(eobject[0][0], with_='lines'))
            for reference in eobject[1]:
                gp('set arrow from %s,%s to %s,%s' % (eobject[0][1][0], eobject[0][1][1], reference[1][0], reference[1][1]))
    
    if len(domain) > 2:
        gp('set ztics 100')
        gp('set zrange [' + str(domain[2][0] - 1) + ':' + str(domain[2][1] + 1) + ']')
        gp.splot(*plots)
    else:
        gp.plot(*plots)   
    gnuPlots.append(gp)
    

###############################################################################
# Prints fragments of graph (object of Structures.GraphStructure type)
# @graphElement : list of graph nodes to print (with their neighbors)
#   
def printObjectGraphElement(graphElement, domain=None, markedObjectsIdx=None):
    gp = Gnuplot.Gnuplot(persist=0) 
            
    if domain is not None:         
        gp('set xrange [' + str(domain[0][0] - 1) + ':' + str(domain[0][1] + 1) + ']')
        gp('set yrange [' + str(domain[1][0] - 1) + ':' + str(domain[1][1] + 1) + ']')
    
    gp('set style arrow 1 head filled size screen 0.03,15,45 lw 3')
    gp('set style arrow 2 head filled size screen 0.03,15,45 ls 1')
    
    plots = []
    for idx, eobject in enumerate(graphElement):            
        if markedObjectsIdx is not None and idx in markedObjectsIdx:
            plots.append(Gnuplot.PlotItems.Data(eobject[0][0], with_='lines lw 3'))
            for reference in eobject[1]:
                plots.append(Gnuplot.PlotItems.Data(reference[0], with_='lines'))
                gp('set arrow arrowstyle 1 from %s,%s to %s,%s' % (eobject[0][1][0], eobject[0][1][1], reference[1][0], reference[1][1]))
        else:
            plots.append(Gnuplot.PlotItems.Data(eobject[0][0], with_='lines'))
            ###################################
            # Iteration through neighbors
            for reference in eobject[1]:
                plots.append(Gnuplot.PlotItems.Data(reference[0], with_='lines'))
                gp('set arrow from %s,%s to %s,%s' % (eobject[0][1][0], eobject[0][1][1], reference[1][0], reference[1][1]))
    
    if domain is not None and len(domain) > 2:
        gp('set ztics 100')
        gp('set zrange [' + str(domain[2][0] - 1) + ':' + str(domain[2][1] + 1) + ']')
        gp.splot(*plots)
    else:
        gp.plot(*plots)   
    gnuPlots.append(gp)
    

###############################################################################
# Prints the result of FuzzyShapeRecognition.getObjectBorderSpectrum function
# The printout is in form of bar chart
def printPolygonCentroidSpectrum(spectrumList):
    # type: (object, object) -> object
    gp = Gnuplot.Gnuplot(persist=0)

    plotData = []
    for spectrum in spectrumList:
        print spectrum
        plotData.append(spectrum[1][0])
    gp('set yrange [0:]')
    gp('set style data histograms')
    gp('set style fill solid 1.0 border -1')
    gp('set ylabel "Distance from centroid"')
    gp('set xlabel "Angle step"')
    gp.plot(Gnuplot.PlotItems.Data(plotData))
    gnuPlots.append(gp)
