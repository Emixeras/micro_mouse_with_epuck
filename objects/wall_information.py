from ePuck_Communication import read_sensors
from objects.sensor_information import SensorInformation

WALL_THRESHHOLD = 1500
WALL_THRESHHOLD_BACK_FRONT = 1500

class WallInformation:
    def __init__(self, front: bool=False, back: bool=False, left: bool=False, right: bool=False):
        self.front = front
        self.back = back
        self.left = left
        self.right = right


    def __str__(self):
        return f"WallInformation(front={self.front}, back={self.back}, left={self.left}, right={self.right})"


def read_walls(ser) -> WallInformation:
    sensors = SensorInformation(read_sensors(ser))
    front = left = right = back = False
    sensors_front = (sensors.front_left + sensors.front_right)/2
    if sensors_front > WALL_THRESHHOLD_BACK_FRONT:
        front = True
    if sensors.left > WALL_THRESHHOLD:
        left = True
    if sensors.right > WALL_THRESHHOLD:
        right = True
    if sensors.back_left > WALL_THRESHHOLD_BACK_FRONT and sensors.back_right > WALL_THRESHHOLD_BACK_FRONT:
        back = True
    return WallInformation(front, back, left, right), sensors
