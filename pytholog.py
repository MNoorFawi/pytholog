import re #, pdb
from copy import deepcopy
from collections import deque 
from functools import wraps #, lru_cache
from itertools import chain
from more_itertools import unique_everseen
from heapq import heappush, heappop

class pl_expr:
    def __init__ (self, fact, prob = None) :
        self._parse_expr(fact, prob)
            
    def _parse_expr(self, fact, prob):
        fact = fact.replace(" ", "")
        self.f = fact
        pred_ind = fact.index("(")
        self.predicate = fact[:pred_ind]
        self.terms = fact[pred_ind:]
        to_remove = str.maketrans("", "", "() ")
        self.terms = self.terms.translate(to_remove).split(",")
        self.prob = prob
        if self.prob:
            self.string = "%s(%s,%.2f)." % (self.predicate, ",".join(self.terms), prob)
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
        self.terms = self.rule_terms(fact)
        if probs: prob_pred = probs[0]
        else: prob_pred = None
        if ":-" in fact: 
            if_ind = fact.index(":-")
            self.lh = pl_expr(fact[:if_ind], prob_pred)
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
            self.fact = (self.lh.to_string() + ":-" + ",".join(rs))
        else:
            self.lh = pl_expr(fact, prob_pred)
            self.rhs = []
            self.fact = self.lh.to_string()
            
    def rule_terms(self, rule_string):
        s = re.sub(" ", "", rule_string)
        s = re.findall('\((.*?)\)', s)
        s = [i.split(",") for i in s]
        s = list(chain(*s))
        return list(unique_everseen(s))

    def to_string(self):
        return self.fact

    def __repr__ (self) :
        return self.fact
    
class goal :
    def __init__ (self, fact, parent = None, domain = {}) :
        self.fact = fact
        self.parent = parent
        self.domain = deepcopy(domain)
        self.ind = 0 

    def __repr__ (self) :
        return "Goal = %s, parent = %s" % (self.fact, self.parent)
        
def unify(lh, rh, lh_domain = None, rh_domain = None):
    if rh_domain == None:
        rh_domain = {} #dict(zip(rh.terms, rh.terms))
    if lh_domain == None:
        lh_domain = {}
    nterms = len(rh.terms)
    if nterms != len(lh.terms): 
        return False
    if rh.predicate != lh.predicate: 
        return False
    for i in range(nterms):
        rh_arg  = rh.terms[i]
        lh_arg = lh.terms[i]
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

class search_queue():
    def __init__(self):
        self._container = deque()
    @property
    def empty(self):
        return not self._container
    def push(self, expr):
        self._container.append(expr)
    def pop(self):
        return self._container.popleft() # FIFO
    def __repr__(self):
        return repr(self._container)
    
class knowledge_base(object):
    _id = 0
    def __init__(self, name = None):
        self.db = {}
        if not name:
            name = "_%d" % knowledge_base._id
            knowledge_base._id += 1
        self.name = name
        
    def add_kn(self, kn):
        for i in kn:
            i = pl_fact(i)
            g = [goal(pl_fact(r.to_string())) for r in i.rhs]
            if i.lh.predicate in self.db:
                self.db[i.lh.predicate]["facts"].append(i)
                self.db[i.lh.predicate]["goals"].append(g)
                self.db[i.lh.predicate]["terms"].append(i.terms)
            else:
                self.db[i.lh.predicate] = {}
                self.db[i.lh.predicate]["facts"] = [i]
                self.db[i.lh.predicate]["goals"] = [g]
                self.db[i.lh.predicate]["terms"] = [i.terms]
            
    def __call__(self, args):
        self.add_kn(args)
            
    def term_checker(self, expr):
        #if not isinstance(expr, pl_expr):
        #    expr = pl_expr(expr)
        terms = expr.terms[:]
        indx = [x for x,y in enumerate(terms) if y <= "Z"]
        for i in indx:
            terms[i] = "Var" + str(i)
        #return expr, "%s(%s)" % (expr.predicate, ",".join(terms))
        return indx, "%s(%s)" % (expr.predicate, ",".join(terms))

    def memory(querizer):
        cache = {}
        @wraps(querizer)
        def memorize_query(self, arg1):
            temp_cache = {}
            #original, look_up = self.term_checker(arg1)
            indx, look_up = self.term_checker(arg1)
            if look_up in cache:
                #return cache[look_up]
                temp_cache = cache[look_up]
            else:
                new_entry = querizer(self, arg1)
                cache[look_up] = new_entry
                temp_cache = new_entry
                #return new_entry
            for d in temp_cache:
                if isinstance(d, dict):
                    old = list(d.keys())
                    #for i in range(len(arg1.terms)):
                    for i,j in zip(indx, range(len(old))):
                        d[arg1.terms[i]] = d.pop(old[j])                      
            return temp_cache    
        return memorize_query

    def querizer(simple_query):
        def wrap(rule_query):
            @wraps(rule_query)
            def prepare_query(self, arg1):
                pred = arg1.predicate
                if pred in self.db:
                    goals_len = 0.0
                    for i in self.db[pred]["goals"]:
                        goals_len += len(i)
                    if goals_len == 0:
                        return simple_query(self, arg1)
                    else:
                        return rule_query(self, arg1)
            return prepare_query 
        return wrap 
    
    def simple_query(self, expr):
        pred = expr.predicate
        result = []
        for i in self.db[pred]["facts"]:
            res = {}
            uni = unify(expr, pl_expr(i.to_string()), res)
            if uni:
                if len(res) == 0: result.append("Yes")
                else: result.append(res)
        if len(result) == 0: result.append("No")
        return result
    
    @memory
    @querizer(simple_query)
    def rule_query(self, expr):
       # pdb.set_trace()
        rule = pl_fact(expr.to_string())
        answer = []
        start = goal(pl_fact("start(search):-from(random_point)"))
        start.fact.rhs = [expr]
        queue = search_queue()
        queue.push(start)
        while not queue.empty:
            current_goal = queue.pop()
            if current_goal.ind >= len(current_goal.fact.rhs):
                if current_goal.parent == None:
                    if current_goal.domain:
                        answer.append(current_goal.domain)
                    else: answer.append("Yes")                      
                    continue
                parent = deepcopy(current_goal.parent)
                unify(parent.fact.rhs[parent.ind],
                      current_goal.fact.lh,
                      parent.domain,
                      current_goal.domain)
                parent.ind += 1
                queue.push(parent)
                continue
                                          
            rule = current_goal.fact.rhs[current_goal.ind]
            if rule.predicate in self.db:
                rule_f = self.db[rule.predicate]
                for f in range(len(rule_f["facts"])):
                    if len(rule.terms) != len(rule_f["facts"][f].lh.terms): continue
                    child = goal(rule_f["facts"][f], current_goal)
                    uni = unify(rule_f["facts"][f].lh, rule,
                                child.domain,
                                current_goal.domain)
                    if uni: queue.push(child)
                                          
        if len(answer) == 0: answer.append("No")    
        return answer
                                          
    def query(self, expr):
        return self.rule_query(expr)

    def __str__(self):
        return "Knowledge Base: " + self.name

    __repr__ = __str__
    
    
