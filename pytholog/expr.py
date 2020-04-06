import re

class pl_expr:
    def __init__ (self, fact):
        self._parse_expr(fact)
            
    def _parse_expr(self, fact):
        fact = fact.replace(" ", "")
        self.f = fact
        splitting = r"is|\*|\+|\-|\/|>=|<=|>|<|and|or|in|not"
        if "(" not in fact: 
            fact = "(" + fact + ")"
        pred_ind = fact.index("(")
        self.predicate = fact[:pred_ind]
        self.terms = fact[pred_ind:]
        to_remove = str.maketrans("", "", "() ")
        self.terms = self.terms.translate(to_remove)
        if self.predicate == "": self.terms = re.split(splitting, self.terms)
        else: self.terms = self.terms.split(",")
        self.string = self.f
    
    ## return string value of the expr in case we need it elsewhere with different type
    def to_string(self):
        return self.string

    def __repr__ (self) :
        return self.string
        