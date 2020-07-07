class MCTSNode(object):
    def __init__(self, move):
        self.num_rollouts = 0 
        self.total_score = 0
        self.move = move    

    def avg_score(self):
        if self.num_rollouts == 0:
            return 0 

        return float(self.total_score) / float(self.num_rollouts)   

    