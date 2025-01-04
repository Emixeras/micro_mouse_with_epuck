from enum import Enum

from ePuck_Communication import connect_to_epuck
from ePuck_Steuerung import *
from ePuck_Walldetection import *


class Cell:
    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column

class direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


class floodfill():
    serobj = {}
    targetcells = []

    cellnow: Cell = Cell(0, 0)
    directionnow = {}

    mazewalls = []
    mazevalues = []
    mazeheight = {}
    mazewidth = {}

    def __init__(self, width, height, targetcells: [Cell])-> None:
        self.serobj = connect_to_epuck()
        self.directionnow = direction.RIGHT
        self.mazeheight = height
        self.mazewidht = width

        self.mazewalls = [[set() for x in range(height)] for x in range(width)]
        self.mazevalues = [[(height * width) for x in range(height)] for x in range(width)]
        for cell in targetcells:
            #TODO was ist hier mit gemeint? Irgendwas stimmt hier nicht. Und was sind targetcells? hab die mal zu cells getyped, weil du hier auch auf index 0 und 1 für row und column zugreifst
            self.mazevalues[cell.row][cell.column] = 0

        # set walls up
        for i in range(width):
            self.mazewalls[i][0].add(direction.UP)
            self.mazewalls[i][-1].add(direction.DOWN)

        for i in range(height):
            self.mazewalls[0][i].add(direction.LEFT)
            self.mazewalls[-1][i].add(direction.RIGHT)

    def floodingmaze(self):
        for roundcounter in range(self.mazeheight * self.mazewidht):
            for i in range(self.mazewidht):
                for j in range(self.mazeheight):
                    if self.mazevalues[i][j] == roundcounter:
                        if (i - 1)>=0:
                            if self.mazevalues[i - 1][j]>(roundcounter + 1):
                                if direction.LEFT not in self.mazewalls[i][j]:
                                    self.mazevalues[i - 1][j] = roundcounter + 1
                        if (j - 1)>=0:
                            if self.mazevalues[i][j - 1]>(roundcounter + 1):
                                if direction.UP not in self.mazewalls[i][j]:
                                    self.mazevalues[i][j - 1] = roundcounter + 1
                        if (i + 1)<self.mazewidht:
                            if self.mazevalues[i + 1][j]>(roundcounter + 1):
                                if direction.RIGHT not in self.mazewalls[i][j]:
                                    self.mazevalues[i + 1][j] = roundcounter + 1
                        if (j + 1)<self.mazeheight:
                            if self.mazevalues[i][j + 1]>(roundcounter + 1):
                                if direction.DOWN not in self.mazewalls[i][j]:
                                    self.mazevalues[i][j + 1] = roundcounter + 1

    def moveOneCell(self):
        move_one_cell_straight(self.serobj)
        if direction.RIGHT == self.directionnow:
            self.cellnow.row = self.cellnow.row + 1
        elif direction.LEFT == self.directionnow:
            self.cellnow.row = self.cellnow.row- 1
        elif direction.DOWN == self.directionnow:
            self.cellnow.column = self.cellnow.column+1
        elif direction.UP == self.directionnow:
            self.cellnow.column = self.cellnow.column-1


    def rotate(self, colockwise = True):
        turn90degree(self.serobj, colockwise)
        if(colockwise):
            self.directionnow = (self.directionnow+1)%4
        else:
            self.directionnow = (self.directionnow-1)%4

    def setWallsToCell(self):
        walls = getWallInformation(self.serobj)
        if walls.front:
            self.mazewalls[self.cellnow.row][self.cellnow.column].add(self.directionnow)
            self.setWallToNeighborCell(self.directionnow)
        if walls.right:
            self.mazewalls[self.cellnow.row][self.cellnow.column].add(self.directionnow + 1)
            self.setWallToNeighborCell(self.directionnow)
        if walls.left:
            self.mazewalls[self.cellnow.row][self.cellnow.column].add(self.directionnow - 1)

    def setWallToNeighborCell(self, directionwall:direction):
        if directionwall == direction.RIGHT:
            if (self.cellnow.row + 1) < self.mazewidht:
                self.mazewalls[self.cellnow.row + 1][self.cellnow.column].add(direction.LEFT)
        elif directionwall == direction.DOWN:
            if (self.cellnow[1] + 1) < self.mazeheight:
                self.mazewalls[self.cellnow.row][self.cellnow.column + 1].add(direction.UP)
        elif directionwall == direction.LEFT:
            if (self.cellnow[0] - 1) > 0:
                self.mazewalls[self.cellnow.row - 1][self.cellnow.column].add(direction.RIGHT)
        elif directionwall == direction.UP:
            if (self.cellnow[1] - 1) > 0:
                self.mazewalls[self.cellnow.row][self.cellnow.column - 1].add(direction.DOWN)

    def searchNCellsLower(self, cellvalue: int)->direction:
        #TODO Check for walls between cells
        if (self.cellnow.row + 1) < self.mazewidht:
            if self.mazevalues[self.cellnow.row + 1][self.cellnow.column] < cellvalue:
                return direction.RIGHT
        if (self.cellnow.column + 1) < self.mazeheight:
            if self.mazevalues[self.cellnow.row][self.cellnow.column + 1] < cellvalue:
                return direction.DOWN
        if (self.cellnow.row - 1) > 0:
            if self.mazevalues[self.cellnow.row - 1][self.cellnow.column] < cellvalue:
                return direction.LEFT
        if (self.cellnow.column - 1)>0:
            if self.mazevalues[self.cellnow.row][self.cellnow.column - 1] < cellvalue:
                return direction.UP

    def moveInMaze(self):
        cellvalue = self.mazevalues[self.cellnow.row][self.cellnow.column]
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
        while self.mazevalues[self.cellnow.row][self.cellnow.column] != 0:
            self.setWallsToCell()
            self.floodingmaze()
            self.moveInMaze()

    def runMaze(self):
        self.cellnow = Cell(0, 0)
        self.directionnow = direction.RIGHT
        while self.mazevalues[self.cellnow.row][self.cellnow.column] != 0:
            self.moveInMaze()