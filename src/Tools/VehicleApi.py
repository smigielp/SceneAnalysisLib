'''
Created on 8 mar 2016

@author: Piter
'''
import numpy as np
from dronekit import *
from time import sleep
from datetime import datetime

#
# mavproxy.py --out 127.0.0.1:14550
# 
# dron = connect('127.0.0.1:14550', wait_ready=True)
from CommandQueue import CommandQueue

from Utils import getCentroid

FRONT = 1
DOWN  = 0
MAX_WAIT_FOR_MODE = 5

class QuadcopterApi(object):
    def __init__(self, connectString='127.0.0.1:14550'):
        print datetime.now(), '- connecting to vehicle...'
        self.quad = connect(connectString, wait_ready=True)
        self.getState()
        self.commandQueue = CommandQueue(self)
    
    def continueAction(self):
        return self.quad.mode.name == VehicleMode('GUIDED')
     
    def close(self):
        self.quad.close()   

    def getDirectionVector(self):
        """
        :return:    normalized vector [east,north,up] of the direction which vehicle is facing
        """
        directionLR = self.quad.heading
        directionUD = 0
        length = 1
        east = math.sin(math.radians(directionLR)) * length
        north = math.cos(math.radians(directionLR)) * length
        up = -math.sin(math.radians(directionUD)) * length
        end = np.array([0.0, 0.0, 0.0])
        end[0] = east
        end[1] = north
        end[2] = up
        return end

    def getPositionVector(self):
        """
        :return:    vector [east,north,up] of position in space or None if vehicle isn't in valid position
        """
        localFrame = self.quad.location.local_frame
        if localFrame.east is None or localFrame.north is None or localFrame.down is None:
            return None
        position = np.array([localFrame.east, localFrame.north, -localFrame.down])

        return position

        
    def getState(self):
        print "  > armed    : ", self.quad.armed
        print "  > location : ", self.quad.location.local_frame  
        print "  > yaw      : ", self.quad.heading

        
    def setMode(self, modeName):
        self.quad.mode = VehicleMode(modeName)
        print datetime.now(), '- Waiting for', modeName, ' mode...'
        waiter = 0
        while self.quad.mode != VehicleMode(modeName):
            sleep(1)
            waiter += 1
            if waiter == MAX_WAIT_FOR_MODE:
                print datetime.now(), '- timeout while waiting for ', modeName, ' mode'
                return
        print datetime.now(), '-', modeName, 'mode set'
        
        
    def arm(self):
        if(not self.quad.armed):
            self.quad.armed = True
            while(not self.quad.armed):
                print datetime.now(), '- waiting for vehicle to arm...'
                sleep(1)                           
                self.quad.armed = True
        else:
            print datetime.now(), '- vehicle already armed'

    
    def takeoff(self, targetAlt=10):
        if targetAlt is None or targetAlt < 0:
            raise RuntimeError("Invalid target altitude provided")
        if targetAlt < 3:
            targetAlt = 3
        if targetAlt < 5:
            print "Dangerously low target altitude during takeoff!"
        self.quad.simple_takeoff(targetAlt-1)
        while True:
            print datetime.now(), 'Altitude:', self.quad.location.global_relative_frame.alt 
            #Break and return from function just below target altitude.        
            if self.quad.location.global_relative_frame.alt>=(targetAlt-1)*0.95:
                print datetime.now(), 'Reached target altitude'
                break
            time.sleep(1)
        self.goto(0,0,1,True)
    
    
    def goto(self, dNorth, dEast, dalt=None, altRelative=False, gdspeed=2.0):
        currentLocation=self.quad.location.global_relative_frame
        if(dalt == None):
            dalt = currentLocation.alt
        elif(altRelative):
            dalt = currentLocation.alt + dalt
        targetLocation=get_location_metres(currentLocation, dNorth, dEast, dalt)
        targetDistance=get_distance_metres(currentLocation, targetLocation)
        self.quad.simple_goto(targetLocation, groundspeed=gdspeed)
    
        while self.continueAction():
            remainingDistance=get_distance_metres(self.quad.location.global_relative_frame, targetLocation)
            print datetime.now(), '- Distance to target:  ', remainingDistance
            if remainingDistance<=0.25:
                print datetime.now(), '- Reached target'
                break;
            sleep(1)
    
    
    def changeHeading(self, heading, relative=True):

        targetHeading = heading%360
        if relative:
            is_relative=1 #yaw relative to direction of travel
            realTargetHeading = (self.quad.heading+heading)%360
        else:
            is_relative=0 #yaw is an absolute angle
            realTargetHeading = heading%360
        print "current: ", self.quad.heading
        print "target:  ", realTargetHeading
        msg = self.quad.message_factory.command_long_encode(
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
            0, #confirmation
            targetHeading,    # param 1, yaw in degrees
            0,          # param 2, yaw speed deg/s
            1,          # param 3, direction -1 ccw, 1 cw
            is_relative, # param 4, relative offset 1, absolute angle 0
            0, 0, 0)    # param 5 ~ 7 not used
        # send command to vehicle
        self.quad.send_mavlink(msg)
        while self.continueAction():
            currentHeading = self.quad.heading
            print datetime.now(), '- Current heading:  ', currentHeading
            if abs(currentHeading - realTargetHeading) <= 2.0:
                print datetime.now(), '- Heading set'
                break

            sleep(1)
     
    def changeAlt(self, targetAlt):    
        msg = self.quad.message_factory.command_long_encode(
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT, #command
            0, #confirmation
            2.0,    # param 1, altitude change rate
            0, 0, 0, 0, 0, 
            targetAlt)               
        # send command to vehicle
        self.quad.send_mavlink(msg)                   
            
            
    def setCameraAim(self, direction):        
        if direction == FRONT:
            print datetime.now(), '- Aiming camera front' 
            self.quad.gimbal.rotate(-50, 0, 0)
        elif direction == DOWN:
            print datetime.now(), '- Aiming camera down' 
            self.quad.gimbal.rotate(-10, 0, 0)
             

    def goto_position_relative(self, north, east, down=0):    
        msg = self.quad.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            #mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # frame
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b0000111111111000, # type_mask (only positions enabled)
            north, east, down,
            0, 0, 0, # x, y, z velocity in m/s  (not used)
            0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
        # send command to vehicle


    def moveForward(self, distance, maintainHeading=True):
        """
        moveForward(self, distance, maintainHeading=True)

        Moves drone by @param distance meters towards direction which it is facing.
        If @param maintainHeading is true, drone will rotate to original direction if it was changed.
        """
        print "moving forward by ", distance
        currentHeading = self.quad.heading
        vec = translate_vec([0,distance], currentHeading)
        east = vec[0]
        north = vec[1]
        self.goto(north,east)
        if maintainHeading:
            print "Setting original heading..."
            self.changeHeading(currentHeading,False)

    def moveToLocRelativeHeading(self, forward, right, maintainHeading=True):
        """
        moveToLocRelativeHeading(self, forward, right, maintainHeading=True)

        Moves drone to the position located @param forward meters forward and @param right meters to the right.
        If @param maintainHeading is true, drone will rotate to original direction if it was changed.
        """
        print "moving by ", forward, ",", right
        heading = self.quad.heading
        vec = translate_vec([right,forward], heading)
        east=vec[0]
        north=vec[1]
        self.goto(north,east)
        #print "Rotating by ",rotateAngle," degrees..."
        #self.changeHeading(rotateAngle)
        #self.moveForward(math.sqrt(forward*forward+right*right),maintainHeading)
        if maintainHeading:
            print "Setting original heading..."
            self.changeHeading(heading,False)
            
def get_location_metres(original_location, dNorth, dEast, dalt):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
    specified `original_location`. The returned LocationGlobal has the same `alt` value
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to 
    the current vehicle position.

    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.

    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius = 6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))
    
    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    targetlocation=LocationGlobalRelative(newlat, newlon, dalt)
    return targetlocation;


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    dalt = aLocation2.alt - aLocation1.alt
    dground = math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5
    return math.sqrt((dground*dground) + (dalt*dalt))

def translate_vec(vec, angle):
    """
    :param vec:
    :param angle:
    :return:        vector
    """
    forward = vec[1]
    right = vec[0]
    distance = math.sqrt(forward*forward+right*right)
    rotateAngle = math.degrees(math.atan2(right,forward))
    currentHeading = (angle+rotateAngle) %360
    east=math.sin(math.radians(currentHeading))*distance
    north=math.cos(math.radians(currentHeading))*distance
    return [east, north]

