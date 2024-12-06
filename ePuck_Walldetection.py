from objects.wall_information import WallInformation
import serial

def getWallInformation(ser: serial.Serial)->WallInformation:
    #TODO getting wall infos

    walls = WallInformation()
    return walls