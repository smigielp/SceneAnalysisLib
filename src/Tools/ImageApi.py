from PIL import Image, ImageTk
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


# Colors used for selective object extraction during vectorization
RED     = "RED"
BLUE    = "BLUE"
YELLOW  = "YELLOW"
MAGENTA = "MAGENTA"

# HSV (Hue, Saturation, Value)
COLOR_BOUNDARY = {
     "RED"        : [[[0, 150, 80], [18, 255, 255]], [[162, 150, 80], [180, 255, 255]]]
    #,"BLUE"       : [[[90, 80, 150], [130, 255, 255]]]
    #,"YELLOW"     : [[[0, 0, 150], [180, 50, 255]], [[20, 50, 150], [40, 255, 255]]]
    #,"YELLOW"     : [[[15, 50, 150], [45, 255, 255]]]
    #,"MAGENTA"    : [[[100, 0, 100], [230, 80, 230]]]
    #"YELLOW"     : [[[20, 50, 80], [40, 255, 255]]]
}

MEDIAN_BLUR = 1


class Filter(object):

    def __init__(self, debugLevel=0):
        self.debugLevel = debugLevel
    
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
        print imagecv.shape
        (h, w) = imagecv.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        rotationMatrix = cv2.getRotationMatrix2D((cX, cY), -90, 1)
        rotationMatrix[0, 2] += (h / 2) - cX
        rotationMatrix[1, 2] += (w / 2) - cY
        newImagecv = cv2.warpAffine(imagecv, rotationMatrix, (h, w))
        print newImagecv.shape
        return newImagecv
               
    
    def showImage(self, imagecv, name="image"):
        cv2.imshow(name, imagecv)
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


    #############################################################################################
    # Image pre-processing 
    #
    def imagePreprocess(self, inputImage):    
        image = inputImage
        #image = cv2.bilateralFilter(inputImage, 11, 90, 90)
        
        #Median Blur
        image = cv2.medianBlur(image, MEDIAN_BLUR)
        
        #Gamma Enhancing  
        gamma = 1.0
        invGamma = 1.0 / gamma
        table = numpy.array([((i / 255.0) ** invGamma) * 255
                             for i in numpy.arange(0, 256)]).astype("uint8") 
        image = cv2.LUT(image, table)
        
        #image = cv2.GaussianBlur(image, (5, 5), 5)
        return image


    #############################################################################################
    # 1) extracts given colors
    # 2) applies edge detection algorithm
    #
    def imageEdgeDetect(self, inputImage, color=None):    
        image = inputImage                  
        hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Extracting all colors
        if color is None:
            fullMask = None
            for selectedColor in COLOR_BOUNDARY.keys():
                for range in COLOR_BOUNDARY[selectedColor]:
                    lower = numpy.array(range[0])
                    upper = numpy.array(range[1])
                    
                    mask = cv2.inRange(hsvImage, lower, upper)
                    if fullMask is None:
                        fullMask = mask
                    else:
                        fullMask = fullMask + mask 
            image = fullMask     
            #image = newImage 
        # Extracting particular color from list
        elif color in COLOR_BOUNDARY.keys():
            fullMask = None       
            for range in COLOR_BOUNDARY[color]:     
                lower = numpy.array(range[0], dtype = "uint8")
                upper = numpy.array(range[1], dtype = "uint8")
                
                mask = cv2.inRange(hsvImage, lower, upper)
                #self.showImage(mask)
                if fullMask is None:
                    fullMask = mask  
                else:
                    fullMask = fullMask + mask
            image = fullMask
        # Extracting objects having similar color to given one (in BGR)
        else:
            found = False
            for selectedColor in COLOR_BOUNDARY.keys():
                for range in COLOR_BOUNDARY[selectedColor]: 
                    if color > range[0] and color < range[1]: 
                        found = True     
                        break
                if found:  
                    fullMask = None  
                    for range in COLOR_BOUNDARY[selectedColor]:
                        lower = numpy.array(range[0], dtype = "uint8")
                        upper = numpy.array(range[1], dtype = "uint8")                    
                        mask = cv2.inRange(hsvImage, lower, upper)
                        if fullMask is None:
                            fullMask = mask
                        else:
                            fullMask = fullMask + mask
                    image = fullMask
                    break
        if self.debugLevel > 1:
            self.showImage(image, "before edging")
        image = cv2.erode(image, numpy.ones((3,3),numpy.uint8),iterations=1)
        image = cv2.Canny(image, 100, 150, 11)        
        return image
    

###############################################################################################
# For use with laptop web camera
class CameraApi(object):          

    def __init__(self, device=1):
        try:
            self.camera = cv2.VideoCapture(device)
            if self.camera.isOpened():
                print "Camera active."
            else:
                print "Camera could not be activated."
        except:
            print "Error opening video capture."
    
    def isOpened(self):
        return self.camera.isOpened()
    
    def getFrame(self):
        try:
            ret, frame = self.camera.read()
        except:
            print "Error getting frame from camera."
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
            return imagecv
        except:
            print "Error getting frame from camera."
        return None
    
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


def PILimageFromArray(array,size,type="RGB",flip=False):
    """
    :param array:   array to parse
    :param size:    width and height tuple
    :param type:    pixels format
    :param flip:    whether image should be flipped afterwards
    :return:        PILimage
    """
    img = Image.fromstring(type, size, array.tostring())
    if flip:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return img

def PILImageToCV(pilImage):
    """
    :param pilImage:    PILimage
    :return:            CVImage
    """
    pilImage = pilImage.convert("RGB")
    open_cv_image = numpy.array(pilImage)
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return open_cv_image

def CVImageFromArray(array,size,type="RGB",flip=False):
    """
    :param array:   array to parse
    :param size:    width and height tuple
    :param type:    pixels format
    :param flip:    whether image should be flipped afterwards
    :return:        CVImage
    """
    img = PILimageFromArray(array,size,type,flip)
    return PILImageToCV(img)