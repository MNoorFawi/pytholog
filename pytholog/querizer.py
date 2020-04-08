from .util import term_checker, get_path, prob_parser
from .fact import Fact
from .expr import Expr
from .goal import Goal
from .unify import unify
from functools import wraps #, lru_cache
from copy import deepcopy
from .pq import SearchQueue

## memory decorator which will be called first once .query() method is called
## it takes the Expr and checks in cache {} whether it exists or not
def memory(querizer):
    #cache = {}
    @wraps(querizer)
    def memorize_query(kb, arg1, cut, show_path):
        temp_cache = {}
        #original, look_up = term_checker(arg1)
        indx, look_up = term_checker(arg1)
        if look_up in kb._cache:
            #return cache[look_up]
            temp_cache = kb._cache[look_up] ## if it already exists return it
        else:
            new_entry = querizer(kb, arg1, cut, show_path)  ## if not give it to querizer decorator
            kb._cache[look_up] = new_entry
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
        def prepare_query(kb, arg1, cut, show_path):
            pred = arg1.predicate
            if pred in kb.db:
                goals_len = 0.0
                for i in kb.db[pred]["goals"]:
                    goals_len += len(i)
                if goals_len == 0:
                    return simple_query(kb, arg1)
                else:
                    return rule_query(kb, arg1, cut, show_path)
        return prepare_query 
    return wrap 

## simple function it unifies the query with the corresponding facts
def simple_query(kb, expr):
    pred = expr.predicate
    result = []
    for i in kb.db[pred]["facts"]:
        res = {}
        uni = unify(expr, Expr(i.to_string()), res)
        if uni:
            if len(res) == 0: result.append("Yes")
            else: result.append(res)
    if len(result) == 0: result.append("No")
    return result

## rule_query() is the main search function
@memory
@querizer(simple_query)
def rule_query(kb, expr, cut, show_path):
    #pdb.set_trace() # I used to trace every step in the search that consumed me to figure out :D
    rule = Fact(expr.to_string()) # change expr to rule class
    answer = []
    path = []
    ## start from a random point (goal) outside the tree
    start = Goal(Fact("start(search):-from(random_point)"))
    ## put the expr as a goal in the random point to connect it with the tree
    start.fact.rhs = [expr]
    queue = SearchQueue() ## start the queue and fill with first random point
    queue.push(start)
    while not queue.empty: ## keep searching until it is empty meaning nothing left to be searched
        current_goal = queue.pop()
        if current_goal.ind >= len(current_goal.fact.rhs): ## all rule goals have been searched
            if current_goal.parent == None: ## no more parents 
                if current_goal.domain:  ## if there is an answer return it
                    answer.append(current_goal.domain)
                    if cut: break
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
            if show_path: path.append(current_goal.domain)
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
            prob_child = Goal(Fact(rule.to_string()),
                              parent = current_goal,
                              domain = current_goal.domain)
            queue.push(prob_child)
            
        elif rule.predicate in kb.db:
            ## search relevant buckets so it speeds up search
            rule_f = kb.db[rule.predicate]
            for f in range(len(rule_f["facts"])): ## loop over corresponding facts
                ## take only the ones with the same predicate and same number of terms
                if len(rule.terms) != len(rule_f["facts"][f].lh.terms): continue
                ## a child goal from the current fact with current goal as parent    
                child = Goal(rule_f["facts"][f], current_goal)
                ## unify current rule fact lh with current goal rhs
                uni = unify(rule_f["facts"][f].lh, rule,
                            child.domain, ## saving in child domain
                            current_goal.domain) ## using current goal domain
                if uni: queue.push(child) ## if unify succeeds add child to queue to be searched
                
    if len(answer) == 0: answer.append("No")  ## if no answers at all return "No"  
                         
    if show_path: 
        path = get_path(kb.db, expr, path)
        return answer, path
    else:
        return answer