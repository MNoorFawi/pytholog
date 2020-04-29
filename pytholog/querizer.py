from .util import term_checker, get_path, prob_parser, is_number, is_variable
from .fact import Fact
from .expr import Expr
from .goal import Goal
from .unify import unify
from functools import wraps #, lru_cache
from .pq import SearchQueue
from .search_util import *

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
    ind = expr.terms[expr.index]
    search_base = kb.db[pred]["facts"]
    result = []
    if not is_variable(ind):
        key = ind
        first, last = fact_binary_search(search_base, key)
    else:
        first, last = (0, len(search_base))
        
    for i in range(first, last):
        res = {}
        uni = unify(expr, Expr(search_base[i].to_string()), res)
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
            
            ## father which is the main rule takes unified child's domain from facts
            child_to_parent(current_goal, queue)
            if show_path: path.append(current_goal.domain)
            continue
        
        ## get the rh expr from the current goal to look for its predicate in database
        rule = current_goal.fact.rhs[current_goal.ind]
        
        ## Probabilities and numeric evaluation
        if rule.predicate == "": ## if there is no predicate
            prob_calc(current_goal, rule, queue)
            continue
            
        elif rule.predicate in kb.db:
            ## search relevant buckets so it speeds up search
            rule_f = kb.db[rule.predicate]["facts"]
            if current_goal.parent == None:
                # parent gets query inputs from grandfather to start search
                parent_inherits(rule, rule_f, current_goal, queue)
            else:
                # a child to search facts in kb
                child_assigned(rule, rule_f, current_goal, queue)
                
    if len(answer) == 0: answer.append("No")  ## if no answers at all return "No"  
                         
    if show_path: 
        path = get_path(kb.db, expr, path)
        return answer, path
    else:
        return answer