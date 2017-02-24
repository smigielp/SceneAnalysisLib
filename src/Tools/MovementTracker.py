from threading import Thread

import math

import GnuplotDrawer
import VehicleApi
from time import sleep

shouldExit = False

def _startTracking(vehicleToTrack):
    xrange = [-4,4]
    hrange = [-2,10]
    points = list()
    points.append([[0, 0, 0]])
    domain=[xrange,xrange,hrange]
    trajectoryGraph = GnuplotDrawer.printMultiPointPicture(points, domain)
    sleep(2)
    while not shouldExit :
        localFrame = vehicleToTrack.quad.location.local_frame
        if (not localFrame.north is None) and (not localFrame.east is None):
            points = list()
            position = [localFrame.east, localFrame.north, -localFrame.down]
            points.append([position])

            pitch = 0
            if not vehicleToTrack.quad.gimbal.pitch is None:
                pitch = vehicleToTrack.quad.gimbal.pitch

            arrow = _getArrowCoordinates(1, position, vehicleToTrack.quad.heading, pitch)
            label = '     [%.1f , %.1f , %.1f]' % (round(position[0],1),round(position[1],1),round(position[2],1))

            GnuplotDrawer.setLabel(trajectoryGraph,arrow[0],label,1)
            GnuplotDrawer.setArrow(trajectoryGraph,arrow,1)
            GnuplotDrawer.setPoints(trajectoryGraph, points)
        sleep(0.5)

def _getArrowCoordinates(length, startPos, directionLR=0, directionUD=0):
    east = math.sin(math.radians(directionLR)) * length
    north = math.cos(math.radians(directionLR)) * length
    up = -math.sin(math.radians(directionUD)) * length
    end = [0, 0, 0]
    end[0] = startPos[0]+east
    end[1] = startPos[1]+north
    end[2] = startPos[2]+up
    result = [startPos, end]
    return result

def start(vehicleToTrack):
    thread = Thread(target=_startTracking, args=(vehicleToTrack,))
    thread.start()
    print "tracking started"

def stop():
    global shouldExit
    shouldExit = True