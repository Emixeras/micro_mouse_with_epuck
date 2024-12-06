from enum import Enum
from objects.wall_information import WallInformation
from ePuck_Steuerung import *
from ePuck_Walldetection import *


class direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


class floodfill():
    serobj = {}
    targetcells = []
    startcell = [0, 0]
    startdirection = {}

    cellnow = [0, 0]
    directionnow = {}

    mazewales = []
    mazevalue = []
    mazehight = {}
    mazewidth = {}

    def __init__(self, walldetectionob, width, hight, targetcells: [])-> None:
        self.serobj = connect_to_epuck()
        self.startdirection = direction.RIGHT
        self.directionnow = direction.RIGHT
        self.mazehight = hight
        self.mazewidht = width

        self.mazewales = [[set() for x in range(hight)] for x in range(width)]
        self.mazevalue = [[(hight*width) for x in range(hight)] for x in range(width)]
        for cell in targetcells:
            self.mazevalue[cell[0]][cell[1]] = 0

        # set walls up
        for i in range(width):
            self.mazewales[i][0].add(direction.UP)
            self.mazewales[i][-1].add(direction.DOWN)

        for i in range(hight):
            self.mazewales[0][i].add(direction.LEFT)
            self.mazewales[-1][i].add(direction.RIGHT)

    def floodingmaze(self):
        for roundcounter in range(self.mazehight*self.mazewidht):
            for i in range(self.mazewidht):
                for j in range(self.mazehight):
                    if(self.mazevalue[i][j] == roundcounter):
                        if((i-1)>=0):
                            if(self.mazevalue[i-1][j]>(roundcounter+1)):
                                if(direction.LEFT not in self.mazewales[i][j]):
                                    self.mazevalue[i-1][j] = roundcounter+1
                        if((j-1)>=0):
                            if(self.mazevalue[i][j-1]>(roundcounter+1)):
                                if(direction.UP not in self.mazewales[i][j]):
                                    self.mazevalue[i][j-1] = roundcounter+1
                        if((i+1)<self.mazewidht):
                            if(self.mazevalue[i+1][j]>(roundcounter+1)):
                                if(direction.RIGHT not in self.mazewales[i][j]):
                                    self.mazevalue[i+1][j] = roundcounter+1
                        if((j+1)<self.mazehight):
                            if(self.mazevalue[i][j+1]>(roundcounter+1)):
                                if(direction.DOWN not in self.mazewales[i][j]):
                                    self.mazevalue[i][j+1] = roundcounter+1
        print("Done")

    def moveOneCell(self):
        moveOneCellStraight(self.serobj)
        if direction.RIGHT == self.directionnow:
            self.cellnow = self.cellnow[0]+1
        elif direction.LEFT == self.directionnow:
            self.cellnow = self.cellnow[0]-1
        elif direction.DOWN == self.directionnow:
            self.cellnow = self.cellnow[1]+1
        elif direction.UP == self.directionnow:
            self.cellnow = self.cellnow[1]-1


    def rotate(self, colockwise = True):
        turn90degree(self.serobj, colockwise)
        if(colockwise):
            self.directionnow = (self.directionnow+1)%4
        else:
            self.directionnow = (self.directionnow-1)%4

    def setWallsToCell(self):
        walls = getWallInformation(self.serobj)
        cell = self.cellnow
        if(walls.front):
            self.mazewales[cell[0]][cell[1]].add(self.directionnow)
            self.setWallToNextCell(self.directionnow)
        if(walls.right):
            self.mazewales[cell[0]][cell[1]].add(self.directionnow+1)
            self.setWallToNextCell(self.directionnow)
        if(walls.left):
            self.mazewales[cell[0]][cell[1]].add(self.directionnow-1)

    def setWallToNextCell(self, directionwall:direction):
        cell = self.cellnow
        if(directionwall == direction.RIGHT):
            if ((cell[0] + 1) < self.mazewidht):
                self.mazewales[cell[0]+1][cell[1]].add(direction.LEFT)
        elif(directionwall == direction.DOWN):
            if ((cell[1] + 1) < self.mazehight):
                self.mazewales[cell[0]][cell[1]+1].add(direction.UP)
        elif(directionwall == direction.LEFT):
            if((cell[0]-1)>0):
                self.mazewales[cell[0]-1][cell[1]].add(direction.RIGHT)
        elif(directionwall == direction.UP):
            if((cell[1]-1)>0):
                self.mazewales[cell[0]][cell[1]-1].add(direction.DOWN)

    def searchNCellsLower(self, cellvalue: int)->direction:
        ##todo
        pass

    def trainMaze(self):
        while(self.mazevalue[self.cellnow[0]][self.cellnow[1]]!=0):
            self.setWallsToCell()
            self.floodingmaze()
            cellvalue = self.mazevalue[self.cellnow[0]][self.cellnow[1]]
            #TODO run to cell



    def runMaze(self):
        pass


obj = floodfill(None, None, 4, 6, [[2,1]])
obj.floodingmaze()


