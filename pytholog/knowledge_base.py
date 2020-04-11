from .util import term_checker, get_path, prob_parser, pl_read
from .fact import Fact
from .expr import Expr
from .goal import Goal
from .unify import unify
from functools import wraps #, lru_cache
from copy import deepcopy
from .pq import SearchQueue
from .querizer import *

## the knowledge base object where we will store the facts and rules
## it's a dictionary of dictionaries where main keys are the predicates
## to speed up searching by looking only into relevant buckets rather than looping over 
## the whole database
class KnowledgeBase(object):
    __id = 0
    def __init__(self, name = None):
        self.db = {}
        if not name:
            name = "_%d" % KnowledgeBase.__id
        self.id = KnowledgeBase.__id
        KnowledgeBase.__id += 1
        self.name = name
        self._cache = {}
    
    ## the main function that adds new entries or append existing ones
    ## it creates "facts", "goals" and "terms" buckets for each predicate
    def add_kn(self, kn):
        for i in kn:
            i = Fact(i)
            ## rhs are stored as Expr here we change class to Goal
            g = [Goal(Fact(r.to_string())) for r in i.rhs]
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

    ## query method will only call rule_query which will call the decorators chain
    ## it is only to be user intuitive readable method                                      
    def query(self, expr, cut = False, show_path = False):
        return rule_query(self, expr, cut, show_path)
        
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

    def from_file(self, file):
        pl_read(self, file)

    def __str__(self):
        return "KnowledgeBase: " + self.name
        
    def clear_cache(self):
        self._cache.clear()

    __repr__ = __str__
    

class DeprecationHelper(object):
    def __init__(self, new_target):
        self.new_target = new_target

    def _warn(self):
        from warnings import warn
        warn("knowledge_base class has been renamed to KnowledgeBase!")

    def __call__(self, *args, **kwargs):
        self._warn()
        return self.new_target(*args, **kwargs)

    def __getattr__(self, attr):
        self._warn()
        return getattr(self.new_target, attr)

knowledge_base = DeprecationHelper(KnowledgeBase)
    