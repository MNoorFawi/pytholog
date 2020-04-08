from .util import rule_terms
import re
from .expr import Expr

class Fact:
    def __init__ (self, fact):
        self._parse_fact(fact)
        
    def _parse_fact(self, fact):
        fact = fact.replace(" ", "")
        self.terms = rule_terms(fact)
        if ":-" in fact: 
            if_ind = fact.index(":-")
            self.lh = Expr(fact[:if_ind])
            replacements = {"),": ")AND", ");": ")OR"}  ## AND OR conditions placeholders
            replacements = dict((re.escape(k), v) for k, v in replacements.items()) 
            pattern = re.compile("|".join(replacements.keys()))
            rh = pattern.sub(lambda x: replacements[re.escape(x.group(0))], fact[if_ind + 2:])
            rh = re.split("AND|OR", rh)
            self.rhs = [Expr(g) for g in rh] 
            rs = [i.to_string() for i in self.rhs]
            self.fact = (self.lh.to_string() + ":-" + ",".join(rs))
        else:   ## to store normal expr as facts as well in the database
            self.lh = Expr(fact)
            self.rhs = []
            self.fact = self.lh.to_string()
    
    ## returning string value of the fact
    def to_string(self):
        return self.fact

    def __repr__ (self) :
        return self.fact
        