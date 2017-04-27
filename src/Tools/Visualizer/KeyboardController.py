import Visualizer

assertion = True


class KeyboardController(object):
    """
    Controls:
        Camera:
            a - move left
            d - move right
            w - move forward
            s - move back
            q - rotate left
            e - rotate right
            r - move up [temporary]
            f - move down [temporary]
        p - print basic debug info
        k - capture current frame and print it
    """
    # todo: process special keys
    # todo: make keys buffered
    def __init__(self, window_):
        if assertion and not isinstance(window_, Visualizer.Visualizer):
            raise RuntimeError("Invalid vehicle provided")
        self.window = window_

    def processKeyboardInput(self, char, x, y):
        window = self.window
        speed = 0.1
        if (char == 'a'):
            window.cameraC.moveFRU(r=-speed)
        if (char == 'd'):
            window.cameraC.moveFRU(r=speed)
        if (char == 'q'):
            window.cameraC.rotate(y=speed)
        if (char == 'e'):
            window.cameraC.rotate(y=-speed)
        if (char == 't'):
            window.cameraC.rotate(x=speed)
        if (char == 'g'):
            window.cameraC.rotate(x=-speed)
        if (char == 'w'):
            window.cameraC.moveFRU(f=speed)
        if (char == 's'):
            window.cameraC.moveFRU(f=-speed)
        if (char == 'r'):
            window.cameraC.moveFRU(u=speed)
        if (char == 'f'):
            window.cameraC.moveFRU(u=-speed)
        if (char == 'p'):
            if window.vehicle is not None:
                print "vehicle: ", window.vehicle.quad.heading, window.vehicle.getPositionVector()
            print  window.cameraC
            print "drone_in_space: ", window.dronePos
            #  print window.cameraC.V
        if (char == 'u'):
            # window._V = Transformations.lookAtMatrix(xyzFrom=np.array([0.,2.,2.]),xyzAtPosition=np.array([0.,0.,0.]))
            window.cameraFromVehicle(not window.isCameraFromVehicle())
            pass
        if (char == 'l'):
            window.vehicle.supressMessages(all= window.vehicle.printCommand)
            pass
        if (char == 'k'):
            from ImageApi import PILimageFromArray
            frame = window.grabFrame()
            img = PILimageFromArray(frame,window.getWindowSize(),"RGBA",True)
            img.show()
            img.save("./screenshot.png")
