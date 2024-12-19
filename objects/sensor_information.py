class SensorInformation:
    def __init__(self, sensors: [int]):
        self.front_right = sensors[0]
        self.front_side_right = sensors[1]
        self.right = sensors[2]
        self.back_right = sensors[3]
        self.back_left = sensors[4]
        self.left = sensors[5]
        self.front_side_left = sensors[6]
        self.front_left = sensors[7]
