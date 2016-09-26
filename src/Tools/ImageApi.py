
import Image, ImageTk
import cv2
import numpy
from VideoCapture import Device


#################################################################################################
# Class with basic image operations 
#
# Overview of functionalities:
# - opening and saving image file
# - getting grayscale images from RGB
# - scaling and mirroring of the images
# - extracting pixels with red color
#



class Filter(object):

    def __init__(self, debugLevel=0):
        self.debugLevel = debugLevel
        pass

    
    ###############################################################################################
    # extracting red color from image and writing new image in the input image
    def extractRedColor(self, image):
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                r = image.item(i, j, 2)
                g = image.item(i, j, 1)
                b = image.item(i, j, 0)
                if r > (g + b):  # z lekkim przesunieciem ku czerwieni
                    image.itemset((i, j, 2), 255)
                    image.itemset((i, j, 1), 255)
                    image.itemset((i, j, 0), 255)
                else:
                    image.itemset((i, j, 2), 0)
                    image.itemset((i, j, 1), 0)
                    image.itemset((i, j, 0), 0)
        return image
        
    
    def convertToBinary(self, image, luminusThreshold=100):
        new_data = []
        for i in range(0, image.shape[1]):
            row = []
            for j in range(0, image.shape[0]):
                luminus = image.item(j, i)
                if luminus > luminusThreshold:  
                    row.append(1)
                else:
                    row.append(0)
            new_data.append(row)
        return new_data
    
   
    def extractWhiteColor(self, image, luminusThreshold):
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                r = image.item(i, j, 2)
                g = image.item(i, j, 1)
                b = image.item(i, j, 0)
                if abs(r - g) < 50 and abs(g - b) < 50 and abs(b - r) < 50 and r + g + b > luminusThreshold: 
                    image.itemset((i, j, 2), 255)
                    image.itemset((i, j, 1), 255)
                    image.itemset((i, j, 0), 255)
                else:
                    image.itemset((i, j, 2), 0)
                    image.itemset((i, j, 1), 0)
                    image.itemset((i, j, 0), 0)
        return image     
     
                 
    def mirrorArrayHorizontally(self, data2D):
        data2D.reverse()
    
            
    def mirrorArrayVertically(self, data2D):
        for row in data2D:
            row.reverse()
         
    
    def rotateImage90Right(self, imagecv):
        rows, cols = imagecv.shape
        rotationMatrix = cv2.getRotationMatrix2D((cols/2, rows/2),-90,1)
        newImagecv = cv2.warpAffine(imagecv, rotationMatrix, (cols, rows))
        return newImagecv
               
    
    def showImage(self, imagecv):
        cv2.imshow("image", imagecv)
        cv2.waitKey()
    
        
    def getImageTkBGR(self, imagecv, width):
        imagecvRGB = cv2.cvtColor(imagecv, cv2.COLOR_BGR2RGBA)
        return self.getImageTk(imagecvRGB, width)     
    
    
    def getImageTkGray(self, imagecv, width):
        imagecvRGB = cv2.cvtColor(imagecv, cv2.COLOR_GRAY2RGBA)
        return self.getImageTk(imagecvRGB, width) 
    
    
    def getImageTk(self, imagecvRGB, width):
        img = Image.fromarray(imagecvRGB)
        img = img.resize((width, img.size[1]*width/img.size[0]))
        imagetk = ImageTk.PhotoImage(img)
        return imagetk
          
          
    def saveFile(self, image, filename):
        image.save(filename)  
            
            
    def loadCvImage(self, filename, resize=1):
        image = cv2.imread(filename)
        return image


    def resizeImage(self, image, resize):
        if resize != 1:
            newX,newY = image.shape[0]*resize, image.shape[1]*resize
            image = cv2.resize(image,(int(newX),int(newY)))
        return image


    def prepareImage(self, image):
        lower1 = numpy.array([0, 0, 30], dtype = "uint8")
        upper1 = numpy.array([10, 10, 255], dtype = "uint8")
        
        lower2 = numpy.array([0, 0, 80], dtype = "uint8")
        upper2 = numpy.array([50, 50, 255], dtype = "uint8")
        
        lower3 = numpy.array([0, 0, 90], dtype = "uint8")
        upper3 = numpy.array([60, 60, 255], dtype = "uint8")
        
        #image = cv2.bilateralFilter(image, 11, 90, 90)
        #image = cv2.medianBlur(image, 5)
        image = cv2.GaussianBlur(image, (5, 5), 0)
       
        mask1 = cv2.inRange(image, lower1, upper1)
        #mask2 = cv2.inRange(image, lower2, upper2)
        mask3 = cv2.inRange(image, lower3, upper3)
        
        image = cv2.add(mask1, mask3)
        #image = cv2.add(image, mask2)
        
        image = cv2.medianBlur(image, 5)
        #image = cv2.Canny(image, 80, 200)
        
        return image
        
                
###############################################################################################
# For use with laptop web camera
class CameraApi(object):          

    def __init__(self):
        try:
            self.camera = cv2.VideoCapture(1)
            if self.camera.isOpened():
                print "Camera active."
            else:
                print "Camera could not be activated."
        except:
            print "Error opening video capture."
        self.filter = Filter()
    
    def isOpened(self):
        return self.camera.isOpened()
    
    def getFrame(self):
        try:
            ret, frame = self.camera.read()
        except:
            print "Error getting frame from camera."
        #self.filter.showPicture(frame)
        return frame
    
    def stopCapture(self):
        try:
            self.camera.release()
        except:
            print "Error stopping video capture."
    
    def release(self):
        try:
            self.camera.release
        except:
            print "Error releasing camera object."
    
    
###############################################################################################
# For use with Video Grabber
class CameraApi2(object):          

    def __init__(self):
        self.camera = Device(0)
    
    def isOpened(self):
        return True
    
    def getFrame(self):
        try:
            PILframe = self.camera.getImage()
            imagecv = cv2.cvtColor(numpy.array(PILframe), cv2.COLOR_BGR2RGB)
        except:
            print "Error getting frame from camera."
        return imagecv
    
    def stopCapture(self):
        try:
            pass
        except:
            print "Error stopping video capture."
    
    def release(self):
        try:
            pass
        except:
            print "Error releasing camera object."
    