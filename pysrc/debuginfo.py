class DebugInfo():
    def __init__(self, humanAI, alienAI, humanShips, alienShips, additionalInfo):
        self.humanAI = humanAI
        self.alienAI = alienAI 
        self.humanShips = humanShips 
        self.alienShips = alienShips 
        self.additionalInfo = additionalInfo 

    def update_ship_count(self, humanShips, alienShips):
        self.humanShips = humanShips 
        self.alienShips = alienShips 

    def update_additional_info(self, additional_info):
        self.additionalInfo = additional_info         
