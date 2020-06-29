from collections import namedtuple 
import enum 

class CollisionSetting(enum.Enum):
    CollisionsOff = 1,
    OnlyEnemyShips = 2,
    AllShips = 3

class MoveToCell():
    def __init__(self, target_cell):
        self.target_cell = target_cell

class MoveFireLeftMissile():
    def __init__(self, target_cell):
        self.target_cell = target_cell

class MoveFireRightMissile():
    def __init__(self, target_cell):
        self.target_cell = target_cell

class MoveFireLaser():
    def __init__(self, target_cell):
        self.target_cell = target_cell

class CommandChangeBearing():
    def __init__(self, target_bearing, is_clockwise):
        self.target_bearing = target_bearing 
        self.is_clockwise = is_clockwise 

class CommandMoveForward():
    def __init__(self, target_cell):
        self.target_cell = target_cell 

class CommandFireLaser():
    def __init__(self):
        pass 

class CommandFireLeftMissile():
    def __init__(self):
        pass 

class CommandFireRightMissile():
    def __init__(self):
        pass 

class Point():
    def __init__(self, x, y):
        self.x = x 
        self.y = y

class Action():
    def __init__(self, type, id, x, y, text):
        self.type = type 
        self.id = id 
        self.x = x 
        self.y = y
        self.text = text         

class Cell(namedtuple('Cell', 'row col')):
    def __eq__(self, other):
        if type(other) is type(self):
            return (self.row == other.row and self.col == other.col) 
        else:
            return False
    
    def neighbors(self):
        return [
            Cell(self.row - 1, self.col - 1),
            Cell(self.row - 1, self.col),
            Cell(self.row - 1, self.col + 1),
            Cell(self.row, self.col - 1),
            Cell(self.row, self.col + 1),
            Cell(self.row + 1, self.col - 1),
            Cell(self.row + 1, self.col),
            Cell(self.row + 1, self.col + 1),
        ]