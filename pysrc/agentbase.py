import math 
from swtypes import Point 
from swtypes import MoveToCell
from swtypes import MoveFireLaser
from swtypes import MoveFireLeftMissile
from swtypes import MoveFireRightMissile
from swtypes import Cell 

class Agent:
    def __init__(self, team, name, position=Point(0, 0), bearing=0):
        self.team = team
        self.name = name
        self.position = position
        self.bearing = 0
        self.left_missile = True 
        self.right_missile = True 
        self.LASER_COOLDOWN = 5   # How many ticks before a laser can be fired again.
        self.last_laser_world_tick = 0
        self.dead = False
        self.health = 90           # About 3 laser hits
        self.commands = []

        self.WIDTH = 35
        self.HEIGHT = 48

    def left_missile_position(self):
        if not self.left_missile:
            return None 

        return self.missile_relative_position(Point(self.position.x - 10, self.position.y + 5))

    def right_missile_position(self):
        if not self.right_missile:
            return None 

        return self.missile_relative_position(Point(self.position.x + 10, self.position.y + 5))
    
    def missile_relative_position(self, missile_point):
        x = missile_point.x
        y = missile_point.y

        angle = (self.bearing) * (math.pi/180);   # Convert to radians
        rotatedX = math.cos(angle) * (x - self.position.x) - math.sin(angle) * (y - self.position.y) + self.position.x;
        rotatedY = math.sin(angle) * (x - self.position.x) + math.cos(angle) * (y - self.position.y) + self.position.y;

        return Point(rotatedX, rotatedY)

    def can_fire_laser(self, game_state):
        if self.last_laser_world_tick + self.LASER_COOLDOWN < game_state.world.world_tick:
            return True 

        return False 

    def can_fire_missile(self, game_state):
        if game_state.world.world_tick <= 15:   # Let's not fire missiles until ships have dispersed a bit. Avoids friendly fire.
            return False 

        return self.left_missile or self.right_missile

    def can_fire_left_missile(self):
        return self.left_missile

    def can_fire_right_missile(self):
        return self.right_missile 

    # Agent can move if it's completed it's last action
    def can_move(self):
        return (len(self.commands) == 0 and not self.dead)  

    def add_command(self, command):
        self.commands.append(command)    

    def current_command(self):
        if len(self.commands) > 0:
            return self.commands[0]
        else:
            return None

    def command_finished(self):
        self.commands.pop(0)

    def kill(self):
        self.commands = []
        self.dead = True

    # This method determines whether or not a particular point touches the ship's collision box, which is the height and width minus 10%
    def is_touched(self, point):
        if self.dead == True:
            return False    # Can't touch a dead thing

        bounding_box_fudge = 1.5  # To approximate collision detection

        x1 = self.position.x - ((self.WIDTH * bounding_box_fudge) / 2.0)
        x2 = self.position.x + ((self.WIDTH * bounding_box_fudge) / 2.0)
        y1 = self.position.y - ((self.HEIGHT * bounding_box_fudge) / 2.0)
        y2 = self.position.y + ((self.HEIGHT * bounding_box_fudge) / 2.0)

        if point.x < x1 or point.x > x2:
            return False 

        if point.y < y1 or point.y > y2:
            return False 

        return True 

    def select_move(self, game_state):
        raise NotImplementedError()