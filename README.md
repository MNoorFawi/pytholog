# pytholog
Python module, a library to be, that enables using prolog logic in python. The aim of the library is to explore ways to use symbolic reasoning with machine learning.

future version will have implementation of logical operators and probability with logics.
pl_query function will be changed totally using probabilities and recursive backtracking but this was a good one to start.

#### Examples

```python
from pytholog import *
```
```python
# test unify function 
var = {}
print(unify(pl_expr("likes(Noor, X)"), pl_expr("likes(noor, Y)"), var, {"Y": ["sausage", "steak"]}))
print(var)

#True
#{'Noor': 'noor', 'X': ['sausage', 'steak']}
```

```python
# construct knowledge base of facts and rules
from pprint import pprint
new_kb = knowledge_base("flavor")
print("KB before filling:")
print(new_kb)
print(new_kb.db)
new_kb(["food_type(gouda, cheese)",
       "food_type(ritz, cracker)",
       "food_type(steak, meat)",
       "food_type(sausage, meat)",
       "food_type(limonade, juice)",
       "food_type(cookie, dessert)",
       "flavor(sweet, dessert)",
       "flavor(savory, meat)",
       "flavor(savory, cheese)",
       "flavor(sweet, juice)",
       "food_flavor(X, Y) :- food_type(X, Z), flavor(Y, Z)"])
print("\nKB after filling:")
pprint(new_kb.db)
print("\nlength: ", len(new_kb.db))

#KB before filling:
#Knowledge Base: flavor
#[]

#KB after filling:
#[food_type(gouda,cheese),
# food_type(ritz,cracker),
# food_type(steak,meat),
# food_type(sausage,meat),
# food_type(limonade,juice),
# food_type(cookie,dessert),
# flavor(sweet,dessert),
# flavor(savory,meat),
# flavor(savory,cheese),
# flavor(sweet,juice),
# food_flavor(X,Y):-food_type(X,Z),flavor(Y,Z)]

#length:  11
```

```python
# searching for variable
pl_query(pl_expr("food_flavor(What, sweet)"), new_kb)

#[{'What': 'cookie'}, {'What': 'limonade'}]
```

```python
# answering questions
pl_query(pl_expr("food_flavor(sausage, savory)"), new_kb)
#['Yes']
```

```python
pl_query(pl_expr("food_flavor(gouda, sweet)"), new_kb)
#[]
```

###### P.S. I wanted to build the whole library from scratch without searching for help or hints. But actually I couldn't :D. I got stuck in the query function, I was using stack structure for backtracking but something was going wrong. all domains were inheriting the output from unify function which led to infinite number of variables. Until I decided to search and after opening lots of links I found a useful trick [here](http://www.openbookproject.net/py4fun/prolog/intro.html). The deepcopy trick of the target domain to keep it independent solved everything. so I used the trick in the query function and modified the unify function.

