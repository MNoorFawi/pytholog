from .util import *

## unify function that will bind variables in the search to their counterparts in the tree
## it takes two pl_expr and try to match the uppercased in lh or lh.domain with their corresponding
## values in rh itself or its domain
def unify(lh, rh, lh_domain = None, rh_domain = None):
    if rh_domain == None:
        rh_domain = {} #dict(zip(rh.terms, rh.terms))
    if lh_domain == None:
        lh_domain = {}
        
    nterms = len(rh.terms)
    if unifiable_check(nterms, rh, lh) == False:
        return False
    
    for i in range(nterms):
        rh_arg  = rh.terms[i]
        lh_arg = lh.terms[i]
        
        if lh_arg == "_": 
            continue
        
        rh_val = rh_val_get(rh_arg, lh_arg, rh_domain)
        
        if rh_val:    # fact or variable in search
            if lh_eval(rh_val, lh_arg, lh_domain) == False:
                return False
    
    return True
    
