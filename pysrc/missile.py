from swtypes import Point 

class Missile():
    def __init__(self, team, name, owner, position=Point(0, 0), bearing=0):
        self.team = team
        self.name = name
        self.owner = owner
        self.position = position
        self.bearing = bearing
        self.damage = 1000
        self.dead = False

    def kill(self):
        self.dead = True