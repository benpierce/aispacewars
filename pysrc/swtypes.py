from collections import namedtuple 
import enum 

class CollisionSetting(enum.Enum):
    CollisionsOff = 1,
    OnlyEnemyShips = 2,
    AllShips = 3

class ScorableAction(enum.Enum):
    Kamikaze = 1,       # Ran into another ship and died 
    Died = 2,           # Died 
    HitByLaser = 3,     # Was hit by a laser (may not have died, but sustained damage)
    TeamLost = 4,       # Team lost the game
    KilledEnemy = 5,    # Killed an enemy
    LaseredEnemy = 6,   # Hit an enemy with laser fire (may not have been fatal)
    Survived = 7,       # Survived to the end
    TeamWon = 8,        # The team won (may not have survived though)
    FriendlyFire = 9    # You killed your teammate with friendly fire :(

class MoveToCell():
    def __init__(self, target_cell):
        self.target_cell = target_cell

    def __str__(self):
         return 'MoveToCell ({0},{1})'.format(self.target_cell.row, self.target_cell.col)

class MoveFireLeftMissile():
    def __init__(self, target_cell):
        self.target_cell = target_cell

    def __str__(self):
         return 'FireLeftMissile ({0}:{1})'.format(self.target_cell.row, self.target_cell.col)

class MoveFireRightMissile():
    def __init__(self, target_cell):
        self.target_cell = target_cell

    def __str__(self):
         return 'FireRightMissile ({0}:{1})'.format(self.target_cell.row, self.target_cell.col)

class MoveFireLaser():
    def __init__(self, target_cell):
        self.target_cell = target_cell

    def __str__(self):
         return 'FireLaser ({0}:{1})'.format(self.target_cell.row, self.target_cell.col)

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