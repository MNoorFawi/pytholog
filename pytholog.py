import re
#from collections import deque 
from functools import wraps #, lru_cache
from itertools import chain
from more_itertools import unique_everseen

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
            if i.lh.predicate in self.db:
                self.db[i.lh.predicate]["facts"].append(i)
                self.db[i.lh.predicate]["goals"].append(i.rhs)
                self.db[i.lh.predicate]["terms"].append(i.terms)
            else: 
                self.db[i.lh.predicate] = {}
                self.db[i.lh.predicate]["facts"] = [i]
                self.db[i.lh.predicate]["goals"] = [i.rhs]
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

    def querizer(query):
        @wraps(query)
        def prepare_query(self, arg1):
            pred = arg1.predicate
            if pred in self.db:
                goals_len = 0.0
                for i in self.db[pred]["goals"]:
                    goals_len += len(i)
                if goals_len == 0:
                    return query(self, arg1)

        return prepare_query    

    @memory
    @querizer    
    def query(self, expr):
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


    def __str__(self):
        return "Knowledge Base: " + self.name

    __repr__ = __str__
    
    
