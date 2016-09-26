from PIL import Image, ImageEnhance
import cv2

#################################################################################################
# Class with basic image operations 
#
# Overview of functionalities:
# - opening and saving image file
# - getting grayscale images from RGB
# - erosion and dilatation
# - scaling and mirroring of the images
# - adding and substracting images
# - bordering algorithms (highlighting borders in the image)
# - extracting pixels with red color
#



class Filter(object):

    def __init__(self, debugLevel=0):
        self.debugLevel = debugLevel
        pass
    
    
    def resizePicture(self, image, resize):
        width = int(image.size[0] * resize)
        height = int(image.size[1] * resize)
        return image.resize((width, height), Image.NEAREST)


    def getBinaryBordersRGB(self, image, luminusThreshold=255, span=None):
        data = image.load()
        if span == None:
            span = max(int(round(max(image.size[0], image.size[1])/400.0)), 1)
            print 'bordering algorithm frame diameter: ', span
        new_data = []
        luminus = luminusThreshold
        for x in range(span, image.size[0] - span):
            row = []
            for y in range(span, image.size[1] - span): 
                # range(image.size[1]-3, 2, -1): #branie zaczynajac od 2 elementu od konca
                r1 = abs(data[x - span, y - span][0] - data[x + span, y + span][0])
                g1 = abs(data[x - span, y - span][1] - data[x + span, y + span][1])
                b1 = abs(data[x - span, y - span][2] - data[x + span, y + span][2])
                r2 = abs(data[x - span, y + span][0] - data[x + span, y - span][0])
                g2 = abs(data[x - span, y + span][1] - data[x + span, y - span][1])
                b2 = abs(data[x - span, y + span][2] - data[x + span, y - span][2])
                if r1 + g1 + b1 >= luminus or r2 + g2 + b2 >= luminus:
                    row.append(1)
                else:
                    row.append(0)
            new_data.append(row)
        return new_data
    
    
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
        dataLen = len(data2D)
        for i in range(int(dataLen / 2)):
            tmp = data2D[i]
            data2D[i] = data2D[dataLen - i - 1]
            data2D[dataLen - i - 1] = tmp
    
            
    def mirrorArrayVertically(self, data2D):
        for row in data2D:
            row.reverse()
        
                   
    def setWeights(self, structElem):
        self.diagonal = type(structElem[0]) is not list
        if self.diagonal:
            self.weights = structElem
        else:
            self.dim = []
            self.dim.append(len(structElem))
            self.dim.append(len(structElem[0]))
            self.weights = {}
            for i in range(self.dim[0]):
                self.weights[i - int(self.dim[0] / 2)] = {}
                for j in range(self.dim[1]):
                    self.weights[i - int(self.dim[0] / 2)][j - int(self.dim[1] / 2)] = structElem[i][j]
            self.sumWeights = 0
            for i in range(len(structElem)):
                self.sumWeights += sum(structElem[i])
            if self.sumWeights == 0:
                self.sumWeights = 1
                
                
    ###############################################################################################      
    # Operacje splotu
    def squareFilter(self, data, x, y):
        pixelSum = 0
        for i in range(-int(self.dim[0] / 2), int(self.dim[0] / 2) + 1):
            for j in range(-int(self.dim[1] / 2), int(self.dim[1] / 2) + 1):
                pixelSum += self.weights[i][j] * data[x + i, y + j]   
        return float(pixelSum) / float(self.sumWeights)
    
    
    
    def diagonalFilter(self, data, x, y):
        summ = self.weights[0] * data[x - 1, y - 1] + self.weights[1] * data[x, y] + self.weights[2] * data[x + 1, y + 1]
        return summ
        
        
    def squareFilterRGB(self, data, x, y):
        r = 0
        g = 0
        b = 0
        sumR = 0
        sumG = 0
        sumB = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                sumR += self.weights[i][j] * data[x + i, y + j][0]
                sumG += self.weights[i][j] * data[x + i, y + j][1]
                sumB += self.weights[i][j] * data[x + i, y + j][2]
                r = int(sumR / self.sumWeights)
                g = int(sumG / self.sumWeights)
                b = int(sumB / self.sumWeights)
        return (r, g, b) 
    
    
    def diagonalFilterRGB(self, data, x, y):
        r = self.weights[0] * data[x - 1, y - 1][0] + self.weights[1] * data[x, y][0] + self.weights[2] * data[x + 1, y + 1][0]
        g = self.weights[0] * data[x - 1, y - 1][1] + self.weights[1] * data[x, y][1] + self.weights[2] * data[x + 1, y + 1][1]
        b = self.weights[0] * data[x - 1, y - 1][2] + self.weights[1] * data[x, y][2] + self.weights[2] * data[x + 1, y + 1][2]
        return (int(r), int(g), int(b))
    
        
    def medianFilterRGB(self, data, x, y):
        rTab = []
        gTab = []
        bTab = []
        for i in range(-int(self.dim[0] / 2), int(self.dim[0] / 2) + 1):
            for j in range(-int(self.dim[1] / 2), int(self.dim[1] / 2) + 1):
                rTab.append(data[x + i, y + j][0])
                gTab.append(data[x + i, y + j][1])
                bTab.append(data[x + i, y + j][2])
        rTab.sort()
        gTab.sort()
        bTab.sort()
        r = rTab[len(rTab) / 2]
        g = gTab[len(gTab) / 2]
        b = bTab[len(bTab) / 2]
        data[x, y] = (r, g, b)
     
     
    def showPicture(self, image):
        image.show()
    
    
    ###############################################################################################
    # Zastosowanie operacji splotu dla przypisanego elem. strukturalnego
    def applySimpleFilter(self, image, structElement):
        self.setWeights(structElement)
        newImage = Image.new(image.mode, image.size)
        if self.diagonal:
            self.applyToImage(image, newImage, self.diagonalFilter)
        else:
            self.applyToImage(image, newImage, self.squareFilter)
        return newImage
    
    
    def applySimpleFilterRGB(self, image, structElement):
        self.setWeights(structElement)
        newImage = Image.new(image.mode, image.size)
        if self.diagonal:
            self.applyToImage(image, newImage, self.diagonalFilterRGB)
        else:
            self.applyToImage(image, newImage, self.squareFilterRGB)
        return newImage
        
           
    ###############################################################################################
    # Converts image to grey scale
    # @shadeCount - number of grey hues 
    #
    def makeBlackWhite(self, image, shadeCount=2):
        newImage = Image.new('L', image.size)
        self.maxLuminus = 255 * 3 + 1       
        self.shadeCount = shadeCount
        self.shadeBounds = [255 * j / (shadeCount - 1) for j in range(shadeCount)]
        self.applyToImage(image, newImage, self.blackWhiteBasicOperator)
        return newImage
    
    ###############################################################################################
    # Converts single colored pixel of the image into grey pixel according
    # to its brightness (the brighter pixel, the brighter grey hue is selected
    #    
    def blackWhiteBasicOperator(self, data, i, j):
        luminus = sum(data[i, j])        
        return self.shadeBounds[min(
                            int(float(luminus) / float(self.maxLuminus) * self.shadeCount),
                            self.shadeCount - 1
                        )]
                
                
    ###############################################################################################
    # SUBSTRACT
    def substractImages(self, im1, im2):
        data1 = im1.load()
        data2 = im2.load()
        newImage = Image.new(im1.mode, im1.size)
        data = newImage.load()
        for i in range(2, im1.size[0] - 2):
            for j in range(2, im1.size[1] - 2):
                rNew = (data1[i, j][0] - data2[i, j][0]) % 256
                gNew = (data1[i, j][1] - data2[i, j][1]) % 256
                bNew = (data1[i, j][2] - data2[i, j][2]) % 256
                data[i, j] = (rNew, gNew, bNew)
        return newImage
    
    
    ###############################################################################################
    # ADD
    def addImages(self, im1, im2):
        data1 = im1.load()
        data2 = im2.load()
        newImage = Image.new(im1.mode, im1.size)
        data = newImage.load()
        for i in range(2, self.image.size[0] - 2):
            for j in range(2, self.image.size[1] - 2):
                rNew = (data1[i, j][0] + data2[i, j][0]) % 256
                gNew = (data1[i, j][1] + data2[i, j][1]) % 256
                bNew = (data1[i, j][2] + data2[i, j][2]) % 256
                data[i, j] = (rNew, gNew, bNew)
        return newImage
     
        
    ###############################################################################################
    # EROSION (morphological operator)
    def erosion(self, image):
        newImage = Image.new(image.mode, image.size)
        self.applyToImage(image, newImage, self.erosionBasicOperator)
        return newImage
                
    def erosionBasicOperator(self, data, i, j):
        n1 = data[i - 1, j - 1]
        n2 = data[i - 1, j]
        n3 = data[i - 1, j + 1]
        n4 = data[i, j - 1]
        n5 = data[i, j + 1]
        n6 = data[i + 1, j - 1]
        n7 = data[i + 1, j]
        n8 = data[i + 1, j + 1]
        return min(data[i, j], n1, n2, n3, n4, n5, n6, n7, n8)      
     
        
    ###############################################################################################
    # DILATATION (morphological operator)
    def dilatation(self, image):
        newImage = Image.new(image.mode, image.size)
        self.applyToImage(image, newImage, self.dilatationBasicOperation)
        return newImage
        
    def dilatationBasicOperation(self, data, i, j):
        n1 = data[i - 1, j - 1]
        n2 = data[i - 1, j]
        n3 = data[i - 1, j + 1]
        n4 = data[i, j - 1]
        n5 = data[i, j + 1]
        n6 = data[i + 1, j - 1]
        n7 = data[i + 1, j]
        n8 = data[i + 1, j + 1]
        return max(data[i, j], n1, n2, n3, n4, n5, n6, n7, n8)
     
     
    ###############################################################################################
    # wykonuje dana funkcje na kazdym pikselu obrazka
    def applyToImage(self, image, new_image, function):
        data = image.load()
        new_data = new_image.load()
        for i in range(2, image.size[0] - 2):
            for j in range(2, image.size[1] - 2):
                new_data[i, j] = function(data, i, j)
   
   

    def loadFile(self, fname, resize=1, openCvImage=True):
        if openCvImage:
            return self.loadCvImage(fname, resize)
        else:
            image = Image.open(fname)
            print 'loaded file: ', image.size, image.mode
            if resize != 1:
                width = int(image.size[0] * resize)
                height = int(image.size[1] * resize)
                image = image.resize((width, height))
                print 'resized image size: ', image.size, image.mode
            return image
         
     
    def saveFile(self, image, fname):
        image.save(fname)  
        
        
    def loadCvImage(self, fname, resize=1):
        image = cv2.imread(fname)
        newX,newY = image.shape[0]*resize, image.shape[1]*resize
        image = cv2.resize(image,(int(newX),int(newY)))
        return image
          
