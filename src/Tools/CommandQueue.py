import VehicleApi


class Command(object):
    def __init__(self, callback, *arguments):
        self._callback = callback
        self._args = arguments

    def execute(self):
        self._callback(*self._args)


class ManouverInfo(object):
    class Type(object):
        UNKNOWN = 0
        MOVE = 1
        ROTATE = 20
        ROTATE_RELATIVE = 21

    def __init__(self):
        self.deltaArg = [0,0,0]
        self.type = None


class CommandQueue(object):
    class Mode(object):
        QUEUE_COMMANDS = 0
        """Mode in which commands will be queued and only executed after confirmation"""
        IMM_EXECUTE = 1
        """Mode in which commands will be executed immediately"""

    def __init__(self, vehicle):
        if not isinstance(vehicle, VehicleApi.QuadcopterApi):
            raise RuntimeError

        self._queue = list()
        self._manouverHistory = list()
        self._vehicle = vehicle
        self._isExecuting = False
        self._shouldStop = False
        self._makeAdjustment = False
        self._mode = CommandQueue.Mode.QUEUE_COMMANDS
        self._startpos = None
        self._startangle = None

    def setMode(self, mode):
        if mode != CommandQueue.Mode.QUEUE_COMMANDS and mode != CommandQueue.Mode.IMM_EXECUTE:
            raise RuntimeError
        self._mode = mode

    def shouldMakeAdjustment(self, b):
        self._makeAdjustment = b

    def stop(self):
        self._shouldStop = True

    def confirm(self):
        if self._isExecuting:
            raise RuntimeError
        localFrame = self._vehicle.quad.location.local_frame
        self._startpos = [localFrame.east, localFrame.north, -localFrame.down]
        self._startangle = [self._vehicle.quad.heading, 0, 0]
        self._executeQueue()
        return

    def addCommand(self, command):
        if self._isExecuting or not isinstance(command, Command):
            raise RuntimeError
        self._queue.append(command)
        if self._mode == CommandQueue.Mode.IMM_EXECUTE:
            self.confirm()
        return

    def addCommands(self, commandsList):
        for command in commandsList:
            self.addCommand(command)
        return

    def addCommandByName(self, commandName, *args):
        if not isinstance(commandName, basestring):
            raise RuntimeError
        print "Executing custom command: ", commandName, args
        callback = getattr(self._vehicle, commandName, None)
        if callback is None:
            print "Invalid command name!"
            return
        nCommand = Command( callback, *args)
        self.addCommand(nCommand)

    def changeHeading(self, heading, relative=True):
        nCommand = Command( self._vehicle.changeHeading, heading, relative)
        self.addCommand(nCommand)

        logEntry = ManouverInfo()
        if not relative:
            logEntry.type = ManouverInfo.Type.ROTATE
        else:
            logEntry.type = ManouverInfo.Type.ROTATE_RELATIVE
        logEntry.deltaArg = [heading,0,0]
        self._manouverHistory.append(logEntry)

        return

    def goto(self, dNorth, dEast, dalt=None, altRelative=False, gdspeed=2.0):
        nCommand = Command( self._vehicle.goto, dNorth, dEast, dalt, altRelative, gdspeed)
        self.addCommand(nCommand)
        return

    def moveForward(self, distance, maintainHeading=True):
        nCommand = Command( self._vehicle.moveForward, distance, maintainHeading)
        self.addCommand(nCommand)
        return

    def moveToLocRelativeHeading(self, forward, right, maintainHeading=True):
        nCommand = Command( self._vehicle.moveToLocRelativeHeading, forward, right, maintainHeading)
        self.addCommand(nCommand)
        return

    def _executeQueue(self):
        if self._isExecuting:
            raise RuntimeError
        self._isExecuting = True
        for command in self._queue:
            if self._shouldStop:
                break
            command.execute()
        if self._makeAdjustment:
            self.makeAdjustment()
        self._queue = list()
        self._isExecuting = False
        return

    def makeAdjustment(self):
        return
