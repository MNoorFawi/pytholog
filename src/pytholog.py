import re#, pdb
from copy import deepcopy
from collections import deque 
from functools import wraps #, lru_cache
from itertools import chain
from more_itertools import unique_everseen
from heapq import heappush, heappop

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
        
class pl_fact:
    def __init__ (self, fact):
        self._parse_fact(fact)
        
    def _parse_fact(self, fact):
        fact = fact.replace(" ", "")
        self.terms = self.rule_terms(fact)
        if ":-" in fact: 
            if_ind = fact.index(":-")
            self.lh = pl_expr(fact[:if_ind])
            replacements = {"),": ")AND", ");": ")OR"}  ## AND OR conditions placeholders
            replacements = dict((re.escape(k), v) for k, v in replacements.items()) 
            pattern = re.compile("|".join(replacements.keys()))
            rh = pattern.sub(lambda x: replacements[re.escape(x.group(0))], fact[if_ind + 2:])
            rh = re.split("AND|OR", rh)
            self.rhs = [pl_expr(g) for g in rh] 
            rs = [i.to_string() for i in self.rhs]
            self.fact = (self.lh.to_string() + ":-" + ",".join(rs))
        else:   ## to store normal expr as facts as well in the database
            self.lh = pl_expr(fact)
            self.rhs = []
            self.fact = self.lh.to_string()
            
    def rule_terms(self, rule_string):  ## getting list of unique terms
        s = re.sub(" ", "", rule_string)
        s = re.findall(r"\((.*?)\)", s)
        s = [i.split(",") for i in s]
        s = list(chain(*s))
        return list(unique_everseen(s))
    
    ## returning string value of the fact
    def to_string(self):
        return self.fact

    def __repr__ (self) :
        return self.fact

## goal class which will help us query the rule branches in the facts tree    
class goal :
    def __init__ (self, fact, parent = None, domain = {}) :
        self.fact = fact
        self.parent = parent  ## parent goal which is a step above in the tree
        ## to keep the domain of the goal independent 
        ## as we will change domains a lot in the search
        self.domain = deepcopy(domain)  
        self.ind = 0 

    def __repr__ (self) :
        return "Goal = %s, parent = %s" % (self.fact, self.parent)

## check whether there is a number in terms or not        
def is_number(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False        

## it parses the operations and returns the keys and the values to be evaluated        
def prob_parser(domain, rule_string, rule_terms):
    if "is" in rule_string:
        s = rule_string.split("is")
        key = s[0]
        value = s[1]
    else:
        key = list(domain.keys())[0]
        value = rule_string
    for i in rule_terms:
        if i in domain.keys():
            value = re.sub(i, str(domain[i]), value)
    value = re.sub(r"(and|or|in|not)", r" \g<0> ", value) ## add spaces after and before the keywords so that eval() can see them
    return key, value

## unify function that will bind variables in the search to their counterparts in the tree
## it takes two pl_expr and try to match the uppercased in lh or lh.domain with their corresponding
## values in rh itself or its domain
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
        if rh_arg <= "Z" and not is_number(rh_arg): 
            rh_val = rh_domain.get(rh_arg)
        else: rh_val = rh_arg
        if rh_val:    # fact or variable in search
            if lh_arg <= "Z" and not is_number(lh_arg):  #variable in destination
                lh_val = lh_domain.get(lh_arg)
                if not lh_val: 
                    lh_domain[lh_arg] = rh_val  
                elif lh_val != rh_val:
                    return False          
            elif lh_arg != rh_val: 
                return False       
    return True

## the queue object we will use to store goals we need to search
## FIFO (First In First Out)
class search_queue():
    def __init__(self):
        self._container = deque()  ## deque() not list [] 
                                   ## the idea is to pop from the left side and deque()
    @property
    def empty(self):
        return not self._container
    def push(self, expr):
        self._container.append(expr)
    def pop(self):
        return self._container.popleft() # FIFO popping from the left O(1)
    def __repr__(self):
        return repr(self._container)

## the knowledge base object where we will store the facts and rules
## it's a dictionary of dictionaries where main keys are the predicates
## to speed up searching by looking only into relevant buckets rather than looping over 
## the whole database
class knowledge_base(object):
    __id = 0
    def __init__(self, name = None):
        self.db = {}
        if not name:
            name = "_%d" % knowledge_base.__id
        self.id = knowledge_base.__id
        knowledge_base.__id += 1
        self.name = name
        self.__cache = {}
    
    ## the main function that adds new entries or append existing ones
    ## it creates "facts", "goals" and "terms" buckets for each predicate
    def add_kn(self, kn):
        for i in kn:
            i = pl_fact(i)
            ## rhs are stored as pl_expr here we change class to goal
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
    
    ## the function that takes care of equalizing all uppercased variables
    def term_checker(self, expr):
        #if not isinstance(expr, pl_expr):
        #    expr = pl_expr(expr)
        terms = expr.terms[:]
        indx = [x for x,y in enumerate(terms) if y <= "Z"]
        for i in indx:
            ## give the same value for any uppercased variable in the same index
            terms[i] = "Var" + str(i)
        #return expr, "%s(%s)" % (expr.predicate, ",".join(terms))
        return indx, "%s(%s)" % (expr.predicate, ",".join(terms))

    ## memory decorator which will be called first once .query() method is called
    ## it takes the pl_expr and checks in cache {} whether it exists or not
    def memory(querizer):
        #cache = {}
        @wraps(querizer)
        def memorize_query(self, arg1):
            temp_cache = {}
            #original, look_up = self.term_checker(arg1)
            indx, look_up = self.term_checker(arg1)
            if look_up in self.__cache:
                #return cache[look_up]
                temp_cache = self.__cache[look_up] ## if it already exists return it
            else:
                new_entry = querizer(self, arg1)  ## if not give it to querizer decorator
                self.__cache[look_up] = new_entry
                temp_cache = new_entry
                #return new_entry
            for d in temp_cache:
                ## temp_cache takes care of changing constant var names in cache
                ## to the variable names use by the user
                if isinstance(d, dict):
                    old = list(d.keys())
                    #for i in range(len(arg1.terms)):
                    for i,j in zip(indx, range(len(old))):
                        d[arg1.terms[i]] = d.pop(old[j])                      
            return temp_cache    
        return memorize_query

    ## querizer decorator is called whenever there's a new query
    ## it wraps two functions: simple and rule query
    ## simple_query() only searched facts not rules while
    ## rule_query() searches rules
    ## this can help speed up search and querizer orchestrate the function to be called
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
    
    ## simple function it unifies the query with the corresponding facts
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

    ## rule_query() is the main search function
    @memory
    @querizer(simple_query)
    def rule_query(self, expr):
        #pdb.set_trace() # I used to trace every step in the search that consumed me to figure out :D
        rule = pl_fact(expr.to_string()) # change expr to rule class
        answer = []
        ## start from a random point (goal) outside the tree
        start = goal(pl_fact("start(search):-from(random_point)"))
        ## put the expr as a goal in the random point to connect it with the tree
        start.fact.rhs = [expr]
        queue = search_queue() ## start the queue and fill with first random point
        queue.push(start)
        while not queue.empty: ## keep searching until it is empty meaning nothing left to be searched
            current_goal = queue.pop()
            if current_goal.ind >= len(current_goal.fact.rhs): ## all rule goals have been searched
                if current_goal.parent == None: ## no more parents 
                    if current_goal.domain:  ## if there is an answer return it
                        answer.append(current_goal.domain)
                    else: 
                        answer.append("Yes") ## if no returns Yes
                    continue ## if no answer found go back to the parent a step above again    
                parent = deepcopy(current_goal.parent) 
                ## deepcopy to keep it unaffected from following unify 
                unify(parent.fact.rhs[parent.ind], ## unify parent goals
                      current_goal.fact.lh,  ## with their children to go step down
                      parent.domain,
                      current_goal.domain)
                parent.ind += 1 ## next rh in the same goal object (lateral move) 
                queue.push(parent) ## add the parent to the queue to be searched
                continue
            
            ## get the rh expr from the current goal to look for its predicate in database
            rule = current_goal.fact.rhs[current_goal.ind]
            
            ## Probabilities and numeric evaluation
            if rule.predicate == "": ## if there is no predicate
                key, value = prob_parser(current_goal.domain, rule.to_string(), rule.terms)
                ## eval the mathematic operation
                value = eval(value)
                if value == True: 
                    value = current_goal.domain.get(key)
                    ## it is true but there is no key in the domain (helpful for ML rules in future)
                    if value is None:
                        value = "Yes"
                elif value == False:
                    value = "No"
                current_goal.domain[key] = value ## assign a new key in the domain with the evaluated value
                prob_child = goal(pl_fact(rule.to_string()),
                                  parent = current_goal,
                                  domain = current_goal.domain)
                queue.push(prob_child)
                
            elif rule.predicate in self.db:
                ## search relevant buckets so it speeds up search
                rule_f = self.db[rule.predicate]
                for f in range(len(rule_f["facts"])): ## loop over corresponding facts
                    ## take only the ones with the same predicate and same number of terms
                    if len(rule.terms) != len(rule_f["facts"][f].lh.terms): continue
                    ## a child goal from the current fact with current goal as parent    
                    child = goal(rule_f["facts"][f], current_goal)
                    ## unify current rule fact lh with current goal rhs
                    uni = unify(rule_f["facts"][f].lh, rule,
                                child.domain, ## saving in child domain
                                current_goal.domain) ## using current goal domain
                    if uni: queue.push(child) ## if unify succeeds add child to queue to be searched
                                          
        if len(answer) == 0: answer.append("No")  ## if no answers at all return "No"  
        
        return answer

    ## query method will only call rule_query which will call the decorators chain
    ## it is only to be user intuitive readable method                                      
    def query(self, expr):
        return self.rule_query(expr)
        
    def rule_search(self, expr):
        if expr.predicate not in self.db:
            return "Rule does not exist!"
        else:
            res = []
            rule_f = self.db[expr.predicate]
            for f in range(len(rule_f["facts"])):
                if len(expr.terms) != len(rule_f["facts"][f].lh.terms): continue
                res.append(rule_f["facts"][f])
        return res

    def __str__(self):
        return "Knowledge Base: " + self.name

    __repr__ = __str__
    
