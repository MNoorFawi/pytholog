from .util import is_number, is_variable

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
        if lh_arg == "_": continue
        if is_variable(rh_arg): 
            rh_val = rh_domain.get(rh_arg)
        else: rh_val = rh_arg
        if rh_val:    # fact or variable in search
            if is_variable(lh_arg):  #variable in destination
                lh_val = lh_domain.get(lh_arg)
                if not lh_val: 
                    lh_domain[lh_arg] = rh_val  
                elif lh_val != rh_val:
                    return False          
            elif lh_arg != rh_val: 
                return False       
    return True
