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

    def __str__(self):
        return (f"Sensor Information:"
                f"Front Right: {self.front_right}"
                f"Front Side Right: {self.front_side_right}"
                f"Right: {self.right}"
                f"Back Right: {self.back_right}"
                f"Back Left: {self.back_left}"
                f"Left: {self.left}"
                f"Front Side Left: {self.front_side_left}"
                f"Front Left: {self.front_left}")
