from threading import Thread
import GnuplotDrawer
import VehicleApi
from time import sleep

shouldExit = False

def _startTracking(vehicleToTrack):
    xrange = [-4,4]
    points = list()
    points.append([[0, 0]])
    domain=[xrange,xrange]
    trajectoryGraph = GnuplotDrawer.printMultiPointPicture(points, domain)
    while not shouldExit :
        localFrame = vehicleToTrack.quad.location.local_frame
        if (localFrame.north != None) and (localFrame.east != None):
            points = list()
            points.append([[localFrame.east, localFrame.north]])
            GnuplotDrawer.setPoints(trajectoryGraph, points)
        sleep(1)

def start(vehicleToTrack):
    thread = Thread(target=_startTracking, args=(vehicleToTrack,))
    thread.start()
    print "tracking started"

def stop():
    global shouldExit
    shouldExit = True