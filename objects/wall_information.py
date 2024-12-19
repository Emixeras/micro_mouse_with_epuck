from ePuck_Communication import read_sensors
from ePuck_Steuerung import WALL_THRESHHOLD, WALL_THRESHHOLD_BACK
from objects.sensor_information import SensorInformation


class WallInformation:
    def __init__(self, front: bool=False, back: bool=False, left: bool=False, right: bool=False):
        self.front = front
        self.back = back
        self.left = left
        self.right = right


    def __str__(self):
        return f"WallInformation(front={self.front}, back={self.back}, left={self.left}, right={self.right})"


def read_walls(ser):
    sensors = SensorInformation(read_sensors(ser))
    front = left = right = back = False
    if sensors.front_right > WALL_THRESHHOLD and sensors.front_left > WALL_THRESHHOLD:
        front = True
    if sensors.left > WALL_THRESHHOLD:
        left = True
    if sensors.right > WALL_THRESHHOLD:
        right = True
    if sensors.back_left > WALL_THRESHHOLD_BACK and sensors.back_right > WALL_THRESHHOLD_BACK:
        back = True
    return WallInformation(front, back, left, right), sensors
