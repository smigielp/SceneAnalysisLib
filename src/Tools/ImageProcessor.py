from SceneRepTools import ModelBuilder3D
from SceneRepTools.Structures import ProjectionSet
from Tools import GnuplotDrawer
from Tools import Utils
from Vectorization.Vectorizer import Vectorizer
import ConfigParser
import ImageApi
import cv2


###########################################################################################
# Class with complex image operations
#
# Overview of functionalities
# - reading algorithms parameters from parameter file
# - vectorization of input image
# - construction of data structure used by 3D model building method
# - 3D model building method (with given ready-to-use data structure or with raw images)
#

# debugLevel:
# 0 - not displaying pictures pictures
# 1 - printing final result of vectorization
# 2 - displaying intermediate pictures of vectorization process (including postprocessing)
# 3 - printing bitmap array [1, 0] on standard output
#

class ImageProcessor(object):
   
    def __init__(self, paramFile=None, configFileSection=None, inDebugLevel=0):                    
        self.config = ConfigParser.RawConfigParser()   
        if configFileSection is not None:   
            self.setAlgorithmsParameters(paramFile, configFileSection)
        self.debugLevel = inDebugLevel  
        
        self.vectorizer = Vectorizer(debugLevel=self.debugLevel)
        self.filter = ImageApi.Filter(debugLevel=self.debugLevel);
        self.mounter = ModelBuilder3D.ModelBuilder3D(distThreshold=1)
                
        
    def setAlgorithmsParameters(self, paramFile, configFileSection):
        self.config.read(paramFile)
        self.erosionRepeat = self.config.getint(configFileSection, "erosionRepeat")
        self.dilatationRepeat = self.config.getint(configFileSection, "dilatationRepeat")
        self.imgResizeScale = self.config.getfloat(configFileSection, "imgResizeScale")        
        # bordering parameters
        self.luminusThreshold = self.config.getint(configFileSection, "luminusThreshold")  
        # vectorization parameters
        self.windowSize = self.config.getint(configFileSection, "windowSize")                 
        self.outlierDistance = self.config.getfloat(configFileSection, "outlierDistance")
        self.closeEdgesDistance = self.config.getfloat(configFileSection, "closeEdgesDistance")       
        # vector postprocessing parameters
        self.straightThreshold = self.config.getint(configFileSection, "straightThreshold")
        self.postprocesLevel = self.config.getint(configFileSection, "postprocesLevel")
        
        
    #############################################################################################
    # Creates vector representation of distinctive shapes on PILImage picture
    # 1) applies given pre-processing (function image Preprocess should include border extraction)
    # 2) mirrors image vertically
    # 3) creates dense sequence of points on object border
    # 4) removes redundant points from border
    #
    def getVectorRepresentation(self, inputImage, imagePreprocess=(lambda img: img)):        
        self.domain = [[0, inputImage.shape[1]], [0, inputImage.shape[0]]]
        self.domain3D = [[0, inputImage.shape[0]]] + self.domain       
        
        self.vectorizer.setParameters(self.windowSize)
        
        self.vectorizer.domain = self.domain
        self.vectorizer.domain3D = self.domain3D
                
        inputImage = imagePreprocess(inputImage)
        
        # Rotation is necessary as the imageCV object has starting point in lower left corner
        # but the algorithms used later read image from upper left corner row-by-row
        image = self.filter.rotateImage90Right(inputImage)
                                                      
        # Extract dense point sequence on the objects contours     
        borderPoints = self.vectorizer.getBorderPointSequence(image, Vectorizer.extractBorderedObject)
            
        if self.debugLevel > 0: 
            GnuplotDrawer.printMultiPointPicture(borderPoints, self.domain)   
        
        imageSizeFactor = (self.domain[0][1] + self.domain[1][1]) / 2
        outlierDist = imageSizeFactor * self.outlierDistance
        closeEdgesDist = imageSizeFactor * self.closeEdgesDistance 
        
        # Remove redundant points from objects contours
        smoothVectors = self.vectorizer.makeSmooth(borderPoints, outlierDist)
        
        smoothVectors = self.vectorizer.vectorPostProcessing(smoothVectors,
                                               combThreshold=closeEdgesDist,
                                               postProcLevel=self.postprocesLevel) 

        if self.debugLevel > 0:
            GnuplotDrawer.printArrowPicture(smoothVectors, self.domain)
               
        return {'vect':smoothVectors, 'domain':self.domain}

    
    #############################################################################################
    # Creates 3D model from the set of images
    # @vectorizedImageSet: [
    #                        [vectorsSet, angle], ...
    #                      ]  
    # angle = None (top), 0 (front), 0.5 (right)
    def create3DStructureFromVectors(self, vectorizedImageSet):
        self.mounter.domain3D = self.domain3D
        #self.mounter.domain3D = [[200,700],[100,550],[150,400]]
        self.mounter.domain2D = self.domain        
        projectionSet = self.extractMainObjects(vectorizedImageSet)         
        # wyswietlenie wszystkich rzutow       
        if self.debugLevel > 0:
            GnuplotDrawer.printVectorPicture([projectionSet.top] + projectionSet.topFeatures, self.domain)
            for proj in projectionSet.wallsProjections:
                GnuplotDrawer.printVectorPicture([proj[0]] + proj[1], self.domain)   
        shapeStructure = self.mounter.create3DStructure(projectionSet)
        return shapeStructure
        
                    
    #############################################################################################
    # Creates data structures for 3D model construction algorithm
    # Extracts the biggest shape in the given set
    # both with "features" - shapes located inside the extracted shape
    #
    def extractMainObjects(self, vectorPictureSet):
        vectorProjectionList = []
        for projection in vectorPictureSet:
            shape = Utils.getLongestVertex(projection[0])
            angle = projection[1]
            # kierunek wektorow dla features odwrocony zeby zaznaczyc pusty obszar
            features = [feature for feature in projection[0] if feature != shape]
            for feature in features:
                feature.reverse()            
            if angle is None:
                topShape = shape
                topFeatures = features
            else:
                vectorProjectionList.append([shape, features, angle])
        projectionSet = ProjectionSet(topProjection=topShape,
                                      topFeatures=topFeatures,
                                      wallsProjectionsList=vectorProjectionList
                                      )
        return projectionSet
                 
