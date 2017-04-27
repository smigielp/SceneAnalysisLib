from threading import Thread

import math

import GnuplotDrawer
import VehicleApi
from time import sleep

shouldExit = False
path = list()
PATH_POINTS_DELAY = 2.

def _startTracking(vehicleToTrack):
    xrange = [-4,4]
    hrange = [-2,30]
    points = list()
    points.append([[0, 0, 0]])
    domain=[xrange,xrange,hrange]
    trajectoryGraph = GnuplotDrawer.printMultiPointPicture(points, domain)
    sleep(2)
    timer = 0.
    while not shouldExit :
        localFrame = vehicleToTrack.quad.location.local_frame
        if (not localFrame.north is None) and (not localFrame.east is None):
            points = list()

            position = vehicleToTrack.getPositionVector()
            points.append([position])

            pitch = 0
            if not vehicleToTrack.quad.gimbal.pitch is None:
                pitch = vehicleToTrack.quad.gimbal.pitch

            arrowHead = position+vehicleToTrack.getDirectionVector()
            arrow = [position,arrowHead]
            label = '     [%.1f , %.1f , %.1f]' % (round(position[0],1),round(position[1],1),round(position[2],1))

            GnuplotDrawer.setLabel(trajectoryGraph,arrow[0],label,1)
            GnuplotDrawer.setArrow(trajectoryGraph,arrow,1)
            GnuplotDrawer.setPoints(trajectoryGraph, points)
            if (timer >= PATH_POINTS_DELAY):
                timer = 0.
                path.append(position)
        sleep(0.5)
        timer += 0.5


def start(vehicleToTrack):
    thread = Thread(name="MovementTrackerThread",target=_startTracking, args=(vehicleToTrack,))
    thread.start()
    print "tracking started"

def stop():
    global shouldExit
    shouldExit = True

def getPath():
    import numpy as np
    global path
    p = np.array(path)
    return p