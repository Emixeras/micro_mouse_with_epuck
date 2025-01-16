from enum import Enum

from ePuck_Communication import connect_to_epuck
from ePuck_Steuerung import *


class Cell:
    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column

class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


class Floodfill():
    serobj = {}
    targetcells = []

    cell_now: Cell = Cell(0, 0)
    direction_now = {}

    mazewalls = []
    mazevalues = []
    mazeheight = {}
    mazewidth = {}


    def __init__(self, serobj, width, height, targetcells: [Cell])-> None:
        self.serobj = serobj
        self.direction_now: Direction = Direction.RIGHT
        self.mazeheight = height
        self.mazewidth = width
        self.targetcells = targetcells
        self.targetcells_original = targetcells
        self.origin = [Cell(0,0)]
        self.mazewalls = [[set() for x in range(height)] for x in range(width)]
        self.mazevalues = [[(height * width) for x in range(height)] for x in range(width)]
        for cell in targetcells:
            self.mazevalues[cell.row][cell.column] = 0

        # set walls up
        for i in range(width):
            self.mazewalls[0][i].add(Direction.UP)
            self.mazewalls[-1][i].add(Direction.DOWN)

        for i in range(height):
            self.mazewalls[i][0].add(Direction.LEFT)
            self.mazewalls[i][-1].add(Direction.RIGHT)

    def floodingmaze(self):
        self.mazevalues = [[(self.mazeheight * self.mazewidth) for x in range(self.mazeheight)] for x in range(self.mazewidth)]
        for cell in self.targetcells:
            self.mazevalues[cell.row][cell.column] = 0

        for roundcounter in range(self.mazeheight * self.mazewidth):
            for i in range(self.mazewidth):
                for j in range(self.mazeheight):
                    if self.mazevalues[i][j] == roundcounter:
                        if (i - 1)>=0:
                            if self.mazevalues[i - 1][j]>(roundcounter + 1):
                                if Direction.UP not in self.mazewalls[i][j]:
                                    self.mazevalues[i - 1][j] = roundcounter + 1
                        if (j - 1)>=0:
                            if self.mazevalues[i][j - 1]>(roundcounter + 1):
                                if Direction.LEFT not in self.mazewalls[i][j]:
                                    self.mazevalues[i][j - 1] = roundcounter + 1
                        if (i + 1)<self.mazewidth:
                            if self.mazevalues[i + 1][j]>(roundcounter + 1):
                                if Direction.DOWN not in self.mazewalls[i][j]:
                                    self.mazevalues[i + 1][j] = roundcounter + 1
                        if (j + 1)<self.mazeheight:
                            if self.mazevalues[i][j + 1]>(roundcounter + 1):
                                if Direction.RIGHT not in self.mazewalls[i][j]:
                                    self.mazevalues[i][j + 1] = roundcounter + 1
        for row in self.mazevalues:
            print(" | ".join(f"{value:2}" for value in row))

    def moveOneCell(self):
        move_one_cell_straight(self.serobj)
        if Direction.RIGHT == self.direction_now:
            self.cell_now.column = self.cell_now.column + 1
        elif Direction.LEFT == self.direction_now:
            self.cell_now.column = self.cell_now.column - 1
        elif Direction.DOWN == self.direction_now:
            self.cell_now.row = self.cell_now.row + 1
        elif Direction.UP == self.direction_now:
            self.cell_now.row = self.cell_now.row - 1


    def rotate(self, colockwise = True):
        turn90degree(self.serobj, colockwise)
        if colockwise:
            self.direction_now = Direction((self.direction_now.value + 1) % 4)
        else:
            self.direction_now = Direction((self.direction_now.value - 1) % 4)

    def setWallsToCell(self):
        walls, _ = read_walls(self.serobj)
        if walls.front:
            self.mazewalls[self.cell_now.row][self.cell_now.column].add(self.direction_now)
            self.setWallToNeighborCell(self.direction_now)
        if walls.right:
            self.mazewalls[self.cell_now.row][self.cell_now.column].add(Direction((self.direction_now.value + 1) % 4))
            self.setWallToNeighborCell(Direction((self.direction_now.value + 1) % 4))
        if walls.left:
            self.mazewalls[self.cell_now.row][self.cell_now.column].add(Direction((self.direction_now.value - 1) % 4))
            self.setWallToNeighborCell(Direction((self.direction_now.value - 1) % 4))


    def setWallToNeighborCell(self, directionwall:Direction):
        if directionwall == Direction.RIGHT:
            if (self.cell_now.column + 1) < self.mazewidth:
                self.mazewalls[self.cell_now.row][self.cell_now.column+1].add(Direction.LEFT)
        elif directionwall == Direction.DOWN:
            if (self.cell_now.row + 1) < self.mazeheight:
                self.mazewalls[self.cell_now.row+1][self.cell_now.column].add(Direction.UP)
        elif directionwall == Direction.LEFT:
            if (self.cell_now.column - 1) > 0:
                self.mazewalls[self.cell_now.row][self.cell_now.column-1].add(Direction.RIGHT)
        elif directionwall == Direction.UP:
            if (self.cell_now.row - 1) > 0:
                self.mazewalls[self.cell_now.row-1][self.cell_now.column].add(Direction.DOWN)

    def searchNCellsLower(self, cellvalue: int)->Direction:
        if (self.cell_now.column + 1) < self.mazewidth:
            if self.mazevalues[self.cell_now.row ][self.cell_now.column + 1] < cellvalue:
                if Direction.RIGHT not in self.mazewalls[self.cell_now.row][self.cell_now.column]:
                    return Direction.RIGHT
        if (self.cell_now.row + 1) < self.mazeheight:
            if self.mazevalues[self.cell_now.row + 1][self.cell_now.column] < cellvalue:
                if Direction.DOWN not in self.mazewalls[self.cell_now.row][self.cell_now.column]:
                    return Direction.DOWN
        if (self.cell_now.column - 1) >= 0:
            if self.mazevalues[self.cell_now.row][self.cell_now.column - 1] < cellvalue:
                if Direction.LEFT not in self.mazewalls[self.cell_now.row][self.cell_now.column]:
                    return Direction.LEFT
        if (self.cell_now.row - 1) >= 0:
            if self.mazevalues[self.cell_now.row - 1][self.cell_now.column] < cellvalue:
                if Direction.UP not in self.mazewalls[self.cell_now.row][self.cell_now.column]:
                    return Direction.UP

    def moveInMaze(self):
        cell_value = self.mazevalues[self.cell_now.row][self.cell_now.column]
        new_direction = self.searchNCellsLower(cell_value)
        now_direction = self.direction_now
        tick_rotate = new_direction.value - now_direction.value
        for i in range(abs(tick_rotate)):
            clockwise = True
            if tick_rotate < 0:
                clockwise = False
            self.rotate(clockwise)
        self.moveOneCell()

    def trainMaze(self):
        while self.mazevalues[self.cell_now.row][self.cell_now.column] != 0:
            self.setWallsToCell()
            self.floodingmaze()
            self.moveInMaze()
        self.targetcells = self.origin
        self.floodingmaze()
        while self.mazevalues[self.cell_now.row][self.cell_now.column] != 0:
            self.setWallsToCell()
            self.floodingmaze()
            self.moveInMaze()
        tick_rotate = Direction.RIGHT.value - self.direction_now.value
        for i in range(abs(tick_rotate)):
            clockwise = True
            if tick_rotate < 0:
                clockwise = False
            self.rotate(clockwise)

        self.targetcells = self.targetcells_original
        self.floodingmaze()
        print("finished")

    def runMaze(self):
        self.cell_now = Cell(0, 0)
        self.direction_now = Direction.RIGHT
        while self.mazevalues[self.cell_now.row][self.cell_now.column] != 0:
            self.moveInMaze()