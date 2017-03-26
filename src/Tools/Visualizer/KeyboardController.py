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
            pass
        if (char == 'k'):
            from ImageApi import imageFromArray
            frame = window.grabFrame()
            img = imageFromArray(frame,window.getWindowSize(),"RGBA",True)
            import cv2
            img.show()
            test = cv2.cvtColor(frame,cv2.COLOR_RGBA2GRAY)
            img = imageFromArray(test,window.getWindowSize(),"L",True)
            img.show()
