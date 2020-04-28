import re
from itertools import chain
from more_itertools import unique_everseen

__all__ = ["is_number", "is_variable", "rh_val_get", "unifiable_check", "lh_eval"] #used in unify module

## a variable is anything that starts with an uppercase letter or is an _
def is_variable(term):
    if is_number(term):
        return False
    elif term <= "Z" or term == "_":
        return True
    else:
        return False
    
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
    
def rule_terms(rule_string):  ## getting list of unique terms
    s = re.sub(" ", "", rule_string)
    s = re.findall(r"\((.*?)\)", s)
    s = [i.split(",") for i in s]
    s = list(chain(*s))
    return list(unique_everseen(s))
    
## the function that takes care of equalizing all uppercased variables
def term_checker(expr):
    #if not isinstance(expr, Expr):
    #    expr = Expr(expr)
    terms = expr.terms[:]
    indx = [x for x,y in enumerate(terms) if y <= "Z"]
    for i in indx:
        ## give the same value for any uppercased variable in the same index
        terms[i] = "Var" + str(i)
    #return expr, "%s(%s)" % (expr.predicate, ",".join(terms))
    return indx, "%s(%s)" % (expr.predicate, ",".join(terms))
    
def get_path(db, expr, path):
    terms = db[expr.predicate]["facts"][0].lh.terms
    path = [{k: i[k] for k in i.keys() if k not in terms} for i in path]
    pathe = [] 
    for i in path:
        for k,v in i.items():
            pathe.append(v)
    return set(pathe)

def pl_read(kb, file):
    file = open(file, "r")
    lines = file.readlines()
    facts = []
    for i in lines:
        i = i.strip()
        i = re.sub(r'\.+$', "", i)
        facts.append(i)
    kb(facts)
    print(f"facts and rules have been added to {kb.name}.db")


def rh_val_get(rh_arg, lh_arg, rh_domain):
    if is_variable(rh_arg):
        rh_val = rh_domain.get(rh_arg)
    else: rh_val = rh_arg
    
    return rh_val
    
def unifiable_check(nterms, rh, lh):
    if nterms != len(lh.terms): 
        return False
    if rh.predicate != lh.predicate: 
        return False
    
def lh_eval(rh_val, lh_arg, lh_domain):
    if is_variable(lh_arg):  #variable in destination
        lh_val = lh_domain.get(lh_arg)
        if not lh_val: 
            lh_domain[lh_arg] = rh_val
            #return lh_domain
        elif lh_val != rh_val:
            return False          
    elif lh_arg != rh_val: 
        return False
