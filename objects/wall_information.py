class WallInformation:
    def __init__(self, front: bool, back: bool, left: bool, right: bool):
        self.front = front
        self.back = back
        self.left = left
        self.right = right

    def __str__(self):
        return f"WallInformation(front={self.front}, back={self.back}, left={self.left}, right={self.right})"
