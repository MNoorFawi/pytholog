#from copy import deepcopy

## goal class which will help us query the rule branches in the facts tree    
class Goal :
    def __init__ (self, fact, parent = None, domain = {}, ind = 0) :
        self.fact = fact
        self.parent = parent  ## parent goal which is a step above in the tree
        ## to keep the domain of the goal independent 
        ## as we will change domains a lot in the search
        self.domain = {}
        self.domain.update(domain)
        self.ind = ind
        
    def __copy__(self):
        return Goal(self.fact, self.parent, self.domain, self.ind)    

    def __repr__ (self) :
        return "Goal = %s, parent = %s" % (self.fact, self.parent)

