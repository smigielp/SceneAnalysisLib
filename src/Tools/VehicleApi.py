'''
Created on 8 mar 2016

@author: Piter
'''
from dronekit import *
from time import sleep
from datetime import datetime

#
# mavproxy.py --out 127.0.0.1:14550
# 
# dron = connect('127.0.0.1:14550', wait_ready=True)

FRONT = 1
DOWN  = 0

class QuadcopterApi(object):    
    
    def __init__(self, connectString='127.0.0.1:14550'):
        self.quad = connect(connectString, wait_ready=True)
    
    def continueAction(self):
        return self.quad.mode.name == VehicleMode('GUIDED')
     
    def close(self):
        self.quad.close()   
    
        
    def getState(self):
        print "  > armed    : ", self.quad.armed
        print "  > location : ", self.quad.location.local_frame  
        print "  > yaw      : ", self.quad.heading

        
    def setMode(self, modeName):
        self.quad.mode = VehicleMode(modeName)
        print datetime.now(), '- Waiting for', modeName, ' mode...'
        while self.quad.mode != VehicleMode(modeName):
            sleep(1)
        print datetime.now(), '-', modeName, 'mode set'
        
        
    def setModeGuided(self):        
        self.setMode('GUIDED')
        if(not self.quad.armed):
            self.quad.armed = True
            while(not self.quad.armed):
                print " Waiting for arming..."
                sleep(1)                           
                self.quad.armed = True
                
    
    def takeoff(self, targetAlt):
        self.quad.simple_takeoff(10)
        while True:
            print datetime.now(), 'Altitude:', self.quad.location.global_relative_frame.alt 
            #Break and return from function just below target altitude.        
            if self.quad.location.global_relative_frame.alt>=targetAlt*0.95: 
                print datetime.now(), 'Reached target altitude'
                break
            time.sleep(1)           
    
    
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
            if remainingDistance<=targetDistance*0.2:
                print datetime.now(), '- Reached target'
                break;
            sleep(1)
    
    
    def changeHeading(self, heading, relative=True):
        if relative:
            is_relative=1 #yaw relative to direction of travel
        else:
            is_relative=0 #yaw is an absolute angle
        targetHeading = (self.quad.heading + heading) % 360
        print "current: ", self.quad.heading
        print "target:  ", targetHeading
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
            print datetime.now(), '- Current heading:  ', self.quad.heading
            if abs(self.quad.heading - targetHeading) <= 2.0:
                print datetime.now(), '- Heading set'
                break;
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
        self.quad.send_mavlink(msg)            
            
            
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
