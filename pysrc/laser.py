from swtypes import Point 

class Laser():
    def __init__(self, team, name, position=Point(0, 0), bearing=0):
        self.team = team
        self.name = name
        self.position = position
        self.bearing = bearing
        self.damage = 30
        self.dead = False

    def kill(self):
        self.dead = True        