from time import sleep

import numpy as np

import VehicleApi


class Command(object):
    def __init__(self, callback, context, *arguments):
        self._callback = callback
        self._args = arguments
        self._context = context

    def execute(self):
        self._callback(*self._args)

    def getManeuverInfo(self):
        info = ManeuverInfo()
        if self._callback == self._context.changeHeading:
            info.type = ManeuverInfo.Type.ROTATE
            heading = self._args[0]
            relative = self._args[1]
            if not relative:
                info.isAbsolute[0] = True
            info.deltaArg[0] = heading
        elif self._callback == self._context.goto:
            dNorth = self._args[0]
            dEast = self._args[1]
            dalt = self._args[2]
            altRelative = self._args[3]
            info.type = ManeuverInfo.Type.MOVE
            info.deltaArg[0] = dEast
            info.deltaArg[1] = dNorth
            info.deltaArg[2] = dalt
            if not altRelative:
                info.isAbsolute[2] = True
        elif self._callback == self._context.moveForward:
            info.type = ManeuverInfo.Type.MOVE_FRU
            distance = self._args[0]
            # maintainHeading = self._args[1]
            info.deltaArg[0] = distance
        elif self._callback == self._context.moveToLocRelativeHeading:
            info.type = ManeuverInfo.Type.MOVE_FRU
            forward = self._args[0]
            right = self._args[1]
            # maintainHeading = self._args[2]
            info.deltaArg[0] = forward
            info.deltaArg[1] = right

        else:
            info.type = ManeuverInfo.Type.UNKNOWN
        return info


class ManeuverInfo(object):
    class Type(object):
        UNKNOWN = 0
        """this maneuver is unknown"""
        IGNORE = 1
        """this maneuver does nothing important - ignore"""
        MOVE = 10
        """move with east,north,up format"""
        MOVE_FRU = 11
        """move with forward,right,up format"""
        ROTATE = 20
        """rotate on (north x east plane),(north x up plane),(None)"""

    def __init__(self):
        self.deltaArg = [0., 0., 0.]
        self.isAbsolute = [False, False, False]
        self.type = None


class CommandQueue(object):
    class Mode(object):
        QUEUE_COMMANDS = 0
        """Mode in which commands will be queued and only executed after confirmation"""
        IMM_EXECUTE = 1
        """Mode in which commands will be executed immediately"""

    def __init__(self, vehicle):
        if not isinstance(vehicle, VehicleApi.QuadcopterApi):
            raise RuntimeError("Invalid argument")

        self._queue = list()
        self._maneuverHistory = list()
        self._vehicle = vehicle
        self._isExecuting = False
        self._shouldStop = False
        self._makeAdjustment = False
        self._mode = CommandQueue.Mode.QUEUE_COMMANDS
        self._startpos = None
        self._startangle = None

    def setMode(self, mode):
        if mode != CommandQueue.Mode.QUEUE_COMMANDS and mode != CommandQueue.Mode.IMM_EXECUTE:
            raise RuntimeError("Invalid argument")
        self._mode = mode

    def shouldMakeAdjustment(self, b):
        self._makeAdjustment = b

    def stop(self):
        self._shouldStop = True

    def confirm(self):
        if self._isExecuting:
            raise RuntimeError("Sent new commands while queue is already executing")
        localFrame = self._vehicle.quad.location.local_frame
        self._startpos = [localFrame.east, localFrame.north, -localFrame.down]
        self._startangle = [float(self._vehicle.quad.heading), 0., 0.]
        self._executeQueue()
        return

    def addCommand(self, command):
        if self._isExecuting or not isinstance(command, Command):
            raise RuntimeError("Invalid argument")
        self._queue.append(command)
        if self._mode == CommandQueue.Mode.IMM_EXECUTE:
            self.confirm()
        return

    def addCommands(self, commandsList):
        for command in commandsList:
            self.addCommand(command)
            self._maneuverHistory.append(command.getManeuverInfo())
        return

    def addCommandByName(self, commandName, *args):
        if not isinstance(commandName, basestring):
            raise RuntimeError("Invalid argument")
        print "Executing custom command: ", commandName, args
        callback = getattr(self._vehicle, commandName, None)
        if callback is None:
            print "Invalid command name!"
            return
        nCommand = Command(callback, self._vehicle, *args)
        self.addCommand(nCommand)
        self._maneuverHistory.append(nCommand.getManeuverInfo())

    def changeHeading(self, heading, relative=True):
        nCommand = Command(self._vehicle.changeHeading, self._vehicle, heading, relative)
        self.addCommand(nCommand)

        self._maneuverHistory.append(nCommand.getManeuverInfo())

        return

    def goto(self, dNorth, dEast, dalt=None, altRelative=False, gdspeed=2.0):
        nCommand = Command(self._vehicle.goto, self._vehicle, dNorth, dEast, dalt, altRelative, gdspeed)
        self.addCommand(nCommand)
        self._maneuverHistory.append(nCommand.getManeuverInfo())
        return

    def moveForward(self, distance, maintainHeading=True):
        nCommand = Command(self._vehicle.moveForward, self._vehicle, distance, maintainHeading)
        self.addCommand(nCommand)
        self._maneuverHistory.append(nCommand.getManeuverInfo())
        return

    def moveToLocRelativeHeading(self, forward, right, maintainHeading=True):
        nCommand = Command(self._vehicle.moveToLocRelativeHeading, self._vehicle, forward, right, maintainHeading)
        self.addCommand(nCommand)
        self._maneuverHistory.append(nCommand.getManeuverInfo())
        return

    def visitPoints(self, points = np.array([]), relativeToStartingPos = False, callbackOnVisited = None,
                    ignoreCallbackResult = False, callbackArg = None):
        if relativeToStartingPos:
            startPos = self._vehicle.getPositionVector()
            for i in range(0,len(points)):
                points[i] = np.array(points[i])
                if len(points[i]) == 2:
                    points[i].resize(3)
                    if relativeToStartingPos:
                        points[i][2] = 0
                    else:
                        points[i][2] = startPos[2]
                points[i] += startPos

        i = 0
        for point in points:
            currPos = self._vehicle.getPositionVector()
            deltaPos = point - currPos
            #if deltaPos[2] != 0:
             #   dalt = deltaPos[2]
            self.goto(deltaPos[1],deltaPos[0],deltaPos[2],True)
            self.confirm()
            i += 1
            if callbackOnVisited is not None:
                if callbackArg is None:
                    if callbackOnVisited(i) and not ignoreCallbackResult:
                        break
                else:
                    if callbackOnVisited(i,callbackArg) and not ignoreCallbackResult:
                        break
        return i

    def _executeQueue(self):
        if self._isExecuting:
            raise RuntimeError("CommandQueue is already executing.")
        self._isExecuting = True
        for command in self._queue:
            if self._shouldStop:
                break
            command.execute()
        if self._makeAdjustment:
            self.makeAdjustment()
        self._queue = list()
        self._maneuverHistory = list()
        self._isExecuting = False
        return

    def makeAdjustment(self):
        targetPos = np.array(self._startpos)
        targetAngle = np.array(self._startangle)
        for m in self._maneuverHistory:
            if not isinstance(m, ManeuverInfo):
                break
            t = m.type
            if t == ManeuverInfo.Type.ROTATE:
                if not m.isAbsolute[0]:
                    targetAngle += m.deltaArg
                else:
                    targetAngle = np.array(m.deltaArg)
            elif t == ManeuverInfo.Type.UNKNOWN:
                print "Adjustment can not be made"
                return
            elif t == ManeuverInfo.Type.IGNORE:
                continue
            elif t == ManeuverInfo.Type.MOVE:
                if m.isAbsolute[0]:
                    targetPos[0] = m.deltaArg[0]
                else:
                    targetPos[0] += m.deltaArg[0]
                if m.isAbsolute[1]:
                    targetPos[1] = m.deltaArg[1]
                else:
                    targetPos[1] += m.deltaArg[1]
                if m.isAbsolute[2]:
                    targetPos[2] = m.deltaArg[2]
                else:
                    targetPos[2] += m.deltaArg[2]
            elif t == ManeuverInfo.Type.MOVE_FRU:
                vec = VehicleApi.translate_vec([m.deltaArg[1], m.deltaArg[0]], targetAngle[0])
                east = vec[0]
                north = vec[1]
                targetPos[0] += east
                targetPos[1] += north
                targetPos[2] += m.deltaArg[2]
        if self._vehicle.printCommand:
            print "targetPos: ", targetPos
            print "targetAngle: ", targetAngle
        sleep(1)
        if self._vehicle.printCommandStatusChecks:
            self._vehicle.getState()
        currPosition = self._vehicle.getPositionVector()
        deltaVector = targetPos - currPosition
        deltaAngle = targetAngle - [self._vehicle.quad.heading, 0, 0]
        if self._vehicle.printCommand:
            print "deltaVector: ", deltaVector
            print "deltaAngle: ", deltaAngle
        self._vehicle.goto(deltaVector[1], deltaVector[0], deltaVector[2], True, 0.3)
        self._vehicle.changeHeading(deltaAngle[0], True)
        return
