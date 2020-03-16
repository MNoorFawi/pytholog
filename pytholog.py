import re, copy
from collections import deque 
from functools import lru_cache

class pl_expr:
    def __init__ (self, fact, prob = None) :
        self._parse_expr(fact, prob)
            
    def _parse_expr(self, fact, prob):
        fact = fact.replace(" ", "")
        self.f = fact
        pred_ind = fact.index("(")
        self.predicate = fact[:pred_ind]
        self.args = fact[pred_ind:]
        to_remove = str.maketrans("", "", "() ")
        self.args = self.args.translate(to_remove).split(",")
        self.prob = prob
        if self.prob:
            self.string = "%s(%s,%.2f)." % (self.predicate, ",".join(self.args), prob)
        else:
            self.string = self.f
        
    def to_string(self):
        return self.string

    def __repr__ (self) :
        return self.string
        
class pl_fact:
    def __init__ (self, fact, probs = None):
        self._parse_fact(fact, probs)
        
    def _parse_fact(self, fact, probs):
        fact = fact.replace(" ", "")
        if probs: prob_pred = probs[0]
        else: prob_pred = None
        if ":-" in fact:
            if_ind = fact.index(":-")
            self.predicate = pl_expr(fact[:if_ind], prob_pred)
        
            replacements = {"),": ")AND", ");": ")OR"}
            replacements = dict((re.escape(k), v) for k, v in replacements.items()) 
            pattern = re.compile("|".join(replacements.keys()))
            rh = pattern.sub(lambda x: replacements[re.escape(x.group(0))], fact[if_ind + 2:])
            rh = re.split("AND|OR", rh)
            if probs and len(probs) > 1:
                self.rhs = [pl_expr(g, p) for g, p in zip(rh, probs[1:])]
            else:
                self.rhs = [pl_expr(g) for g in rh]
        
            rs = [i.to_string() for i in self.rhs]
            self.fact = (self.predicate.to_string() + ":-" + ",".join(rs))
        else:
            self.predicate = pl_expr(fact, prob_pred)
            self.rhs = []
            self.fact = self.predicate.to_string()

    def to_string(self):
        return self.fact

    def __repr__ (self) :
        return self.fact
        
def unify(lh, rh, lh_domain = None, rh_domain = None):
    if rh_domain == None:
        rh_domai = dict(zip(rh.args, rh.args))
    if lh_domain == None:
        lh_domain = {}
    nargs = len(rh.args)
    if nargs != len(lh.args): 
        return False
    if rh.predicate != lh.predicate: 
        return False
    for i in range(nargs):
        rh_arg  = rh.args[i]
        lh_arg = lh.args[i]
        if rh_arg <= 'Z': 
            rh_val = rh_domain.get(rh_arg)
        else: rh_val = rh_arg
        if rh_val:    # fact or variable in search
            if lh_arg <= 'Z':  #variable in destination
                lh_val = lh_domain.get(lh_arg)
                if not lh_val: 
                    lh_domain[lh_arg] = rh_val  
                elif lh_val != rh_val:
                    return False          
            elif lh_arg != rh_val: 
                return False       
    return True
    
class knowledge_base(object):
    _id = 0
    def __init__(self, name = None):
        self.db = []
        if not name:
            name = "_%d" % knowledge_base._id
            knowledge_base._id += 1
        self.name = name
        
    def add_kn(self, kn):
        #kns = tuple(kn)
        for i in kn:
            self.db.append(pl_fact(i))
            
    def __call__(self, args):
        self.add_kn(args)
        
    def __str__(self):
        return "Knowledge Base: " + self.name

    __repr__ = __str__
    
class target: 
    _id = 0
    def __init__(self, fact, supertarget = None, domain = {}):
        self.id = target._id
        target._id += 1
        self.fact = fact
        self.supertarget = supertarget
        self.domain = copy.deepcopy(domain) # to keep every target domain independent
        self.dir = 0      # start search with 1st subtarget

    def __repr__ (self) :
        return "fact=%s\ngoals=%s\ndomain=%s" % (self.fact, self.fact.rhs, self.domain)
        
def find_indices(lst, condition):
    return [i for i, elem in enumerate(lst) if condition(elem)]

@lru_cache(maxsize = None)
def pl_query(pl_expr, kb):
    #var = find_indices(pl_expr.args, lambda e: e <= "Z")
    answer = []
    tgt = target(pl_fact("start(search):-from(random)"))      # start randomly
    tgt.fact.rhs = [pl_expr]                  
    stack = deque([tgt])                            # Start our search
    while stack:
        nxt_tgt = stack.pop()        # Next target to consider
        if nxt_tgt.dir >= len(nxt_tgt.fact.rhs) :       # finished?
            if nxt_tgt.supertarget == None :             
                if nxt_tgt.domain: answer.append(nxt_tgt.domain)
                else: answer.append("Yes")        # have a solution or yes
                continue
            supertgt = copy.deepcopy(nxt_tgt.supertarget)  # go one step above in the tree
            unify(supertgt.fact.rhs[supertgt.dir],
                  nxt_tgt.fact.predicate,
                  supertgt.domain,
                  nxt_tgt.domain)
            supertgt.dir += 1         # next goal
            stack.append(supertgt)          
            continue

        # unify in the database
        pl_expr = nxt_tgt.fact.rhs[nxt_tgt.dir]            
        for kn in kb.db:                     
            if kn.predicate.predicate != pl_expr.predicate: continue
            if len(kn.predicate.args) != len(pl_expr.args): continue
            subtarget = target(kn, nxt_tgt)               # A possible subtarget
            ans = unify(kn.predicate, pl_expr, 
                        subtarget.domain,
                        nxt_tgt.domain)
            if ans:                            # if unifies, stack it up
                stack.append(subtarget)
        
    return answer
    
    
