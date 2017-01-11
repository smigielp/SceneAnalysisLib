import Gnuplot


############################################################################################
# Printing 2D and 3D objects in Gnuplot diagrams
#


gnuPlots = []  
domain3D = None  

gp = Gnuplot.Gnuplot(persist=0)
           
def printMultiPointPicture(mapToPrint, domain):
    #gp = Gnuplot.Gnuplot(persist=0)
    gp('set xrange [' + str(domain[0][0] - 1) + ':' + str(domain[0][1] + 1) + ']')
    gp('set yrange [' + str(domain[1][0] - 1) + ':' + str(domain[1][1] + 1) + ']')
    
    plots = []
    for pointList in mapToPrint:  
        plots.append(Gnuplot.PlotItems.Data(pointList))
    if len(domain) > 2:
        gp.splot(*plots)
    else:
        gp.plot(*plots)  
    gnuPlots.append(gp)   
   
        
def printVectorPicture(mapToPrint, domain):   
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
    
