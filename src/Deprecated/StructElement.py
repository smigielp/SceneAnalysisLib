
#==============================================
# przykladowe elementy strukturalne
#==============================================
basicFrame = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
basicFrame2 = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
moveFilter1 = [[1, 0, 0, ], [0, -1, 0], [0, 0, 0]]
moveFilter2 = [[-1, 0, 0, ], [0, 1, 0], [0, 0, 0]]
highFilter = [[-1, -1, -1], [-1, 14, -1], [-1, -1, -1]]
diagFilter = [1, -1, 0]  









'''
class BaseElement(object):
    
    def _init_(self, wgt, diagonal = False):
        self.weights = wgt
        self.diagonal = diagonal
        if diagonal == False:
            self.setWeights(wgt)
        
    def set_weights(self, wgt):
        self.setWeights(wgt)
        
    def setWeights(self, wgt):
        self.dim = []
        self.dim.append(len(wgt))
        self.dim.append(len(wgt[0]))
        self.weights = {}
        for i in range(self.dim[0]):
            self.weights[i-int(self.dim[0] / 2)] = {}
            for j in range(self.dim[1]):
                self.weights[i-int(self.dim[0] / 2)][j- int(self.dim[1] / 2)] = wgt[i][j]
        self.sumWeights = 0
        for i in range(len(wgt)):
            self.sumWeights += sum(wgt[i])
        if self.sumWeights == 0:
            self.sumWeights = 1
    
        
    # Operacje splotu
    
    def squareFilter(self, data, x, y):
        sum = 0
        for i in range(-int(self.dim[0] / 2), int(self.dim[0] / 2)+1):
            for j in range(-int(self.dim[1] / 2), int(self.dim[1] / 2)+1):
                sum += self.weights[i][j] * data[x + i, y + j]   
        return float(sum) / float(self.sumWeights)
    
    #============================
    # eksperyment
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
        #for i in range(-int(self.dim[0] / 2), int(self.dim[0] / 2)+1):
        #    for j in range(-int(self.dim[1] / 2), int(self.dim[1] / 2)+1):
        # oszczedniejsze:
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
        for i in range(-int(self.dim[0] / 2), int(self.dim[0] / 2)+1):
            for j in range(-int(self.dim[1] / 2), int(self.dim[1] / 2)+1):
                rTab.append(data[x + i, y + j][0])
                gTab.append(data[x + i, y + j][1])
                bTab.append(data[x + i, y + j][2])
        rTab.sort()
        gTab.sort()
        bTab.sort()
        r = rTab[len(rTab)/2]
        g = gTab[len(gTab)/2]
        b = bTab[len(bTab)/2]
        data[x, y] = (r, g, b)
 '''       
