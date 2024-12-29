from enum import Enum

from ePuck_Communication import connect_to_epuck
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

    cellnow = [0, 0]
    directionnow = {}

    mazewalls = []
    mazevalues = []
    mazehight = {}
    mazewidth = {}

    def __init__(self, width, hight, targetcells: [])-> None:
        self.serobj = connect_to_epuck()
        self.directionnow = direction.RIGHT
        self.mazehight = hight
        self.mazewidht = width

        self.mazewalls = [[set() for x in range(hight)] for x in range(width)]
        self.mazevalues = [[(hight * width) for x in range(hight)] for x in range(width)]
        for cell in targetcells:
            self.mazevalues[cell[0]][cell[1]] = 0

        # set walls up
        for i in range(width):
            self.mazewalls[i][0].add(direction.UP)
            self.mazewalls[i][-1].add(direction.DOWN)

        for i in range(hight):
            self.mazewalls[0][i].add(direction.LEFT)
            self.mazewalls[-1][i].add(direction.RIGHT)

    def floodingmaze(self):
        for roundcounter in range(self.mazehight*self.mazewidht):
            for i in range(self.mazewidht):
                for j in range(self.mazehight):
                    if(self.mazevalues[i][j] == roundcounter):
                        if((i-1)>=0):
                            if(self.mazevalues[i - 1][j]>(roundcounter + 1)):
                                if(direction.LEFT not in self.mazewalls[i][j]):
                                    self.mazevalues[i - 1][j] = roundcounter + 1
                        if((j-1)>=0):
                            if(self.mazevalues[i][j - 1]>(roundcounter + 1)):
                                if(direction.UP not in self.mazewalls[i][j]):
                                    self.mazevalues[i][j - 1] = roundcounter + 1
                        if((i+1)<self.mazewidht):
                            if(self.mazevalues[i + 1][j]>(roundcounter + 1)):
                                if(direction.RIGHT not in self.mazewalls[i][j]):
                                    self.mazevalues[i + 1][j] = roundcounter + 1
                        if((j+1)<self.mazehight):
                            if(self.mazevalues[i][j + 1]>(roundcounter + 1)):
                                if(direction.DOWN not in self.mazewalls[i][j]):
                                    self.mazevalues[i][j + 1] = roundcounter + 1

    def moveOneCell(self):
        move_one_cell_straight(self.serobj)
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
        if walls.front:
            self.mazewalls[cell[0]][cell[1]].add(self.directionnow)
            self.setWallToNeighborCell(self.directionnow)
        if walls.right:
            self.mazewalls[cell[0]][cell[1]].add(self.directionnow + 1)
            self.setWallToNeighborCell(self.directionnow)
        if walls.left:
            self.mazewalls[cell[0]][cell[1]].add(self.directionnow - 1)

    def setWallToNeighborCell(self, directionwall:direction):
        cell = self.cellnow
        if directionwall == direction.RIGHT:
            if (cell[0] + 1) < self.mazewidht:
                self.mazewalls[cell[0] + 1][cell[1]].add(direction.LEFT)
        elif directionwall == direction.DOWN:
            if (cell[1] + 1) < self.mazehight:
                self.mazewalls[cell[0]][cell[1] + 1].add(direction.UP)
        elif directionwall == direction.LEFT:
            if (cell[0] - 1)>0:
                self.mazewalls[cell[0] - 1][cell[1]].add(direction.RIGHT)
        elif directionwall == direction.UP:
            if (cell[1] - 1)>0:
                self.mazewalls[cell[0]][cell[1] - 1].add(direction.DOWN)

    def searchNCellsLower(self, cellvalue: int)->direction:
        cell = self.cellnow
        #TODO Check for walls between cells
        row_index = cell[0]
        column_index = cell[1]
        if (row_index + 1) < self.mazewidht:
            if self.mazevalues[row_index + 1][column_index] < cellvalue:
                return direction.RIGHT
        if (column_index + 1) < self.mazehight:
            if self.mazevalues[row_index][column_index + 1] < cellvalue:
                return direction.DOWN
        if (row_index - 1) > 0:
            if self.mazevalues[row_index - 1][column_index] < cellvalue:
                return direction.LEFT
        if (column_index - 1)>0:
            if self.mazevalues[row_index][column_index - 1] < cellvalue:
                return direction.UP

    def moveInMaze(self):
        cellvalue = self.mazevalues[self.cellnow[0]][self.cellnow[1]]
        newdirection = self.searchNCellsLower(cellvalue)
        nowdirection = self.directionnow
        tickrotate = newdirection.value - nowdirection.value
        for i in range(abs(tickrotate)):
            clockwise = True
            if tickrotate < 0:
                clockwise = False
            self.rotate(clockwise)
        self.moveOneCell()

    def trainMaze(self):
        while self.mazevalues[self.cellnow[0]][self.cellnow[1]] != 0:
            self.setWallsToCell()
            self.floodingmaze()
            self.moveInMaze()

    def runMaze(self):
        self.cellnow = [0, 0]
        self.directionnow = direction.RIGHT
        while self.mazevalues[self.cellnow[0]][self.cellnow[1]] != 0:
            self.moveInMaze()