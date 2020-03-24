pytholog
================

## Prolog in Python

Python module, a library to be, that enables using prolog logic in
python. The aim of the library is to explore ways to use symbolic
reasoning with machine learning.

future version will have implementation of logical operators and
probability with logics.

###### OR can be implemented with defining the rules as many times as the OR facts. For example, to say "fly(X) :- bird(X) ; wings(X)." can be defined as two rules as follows: "fly(X) :- bird(X)." and "fly(X) :- wings(X)."

#### prolog syntax

![](pytholog_files/figure-gfm/prolog_ex.png)

Prolog takes facts and rules. A fact or a rule has a predicate which in
“likes(noor, sausage)” is “likes” and in “friend(X, Y)” is “friend”.
Rules have “Left Hand Side (LHS)” which has a predicate and “Right Hand
Sides (RHS)” or “goals” to be searched to answer the queries about the
rules. LHS and RHS in a rule are separated with “:-”. Each predicate has
“Terms”. Prolog uses lowercased variables to describe “constant values”
and uppercased values to describe “variables” that need to be updated
from the query.

Let’s take an example: **likes(noor, sausage)** is a fact which has
**likes** as a predicate and **(noor and sausage)** as terms.
**friend(X, Y) :- +(X = Y), likes(X, Z), likes(Y, Z)** is a rule which
defines that two persons are considered friends if they like the same
dish. This rule has an LHS **friend(X, Y)** and RHS or goals **\[+(X =
Y), likes(X, Z), likes(Y, Z)\]**. The comma separating the goals means
**and** while **;** will mean **or**. Variables in the fact are
lowercased meaning they are truths and cannot change. While in a rule
they are Uppercased meaning they need to be changed while in a query.

Prolog uses **backtracking** search to answer the questions and the
queries.

I loved prolog and the idea of Symbolic Intelligence. So I decided to
build a module or a framework in python that can allow me to use prolog
inside python aiming to combine the power of machine learning and
symbolic reasoning.

#### pytholog Implementation

``` python
import pytholog as pl
```

#### Defining a knowledge base object to store the facts and rules.

``` python
from pprint import pprint
new_kb = pl.knowledge_base("flavor")
print("KB before filling:")
print(new_kb)
print(new_kb.db)
new_kb(["likes(noor, sausage)",
        "likes(melissa, pasta)",
        "likes(dmitry, cookie)",
        "likes(nikita, sausage)",
        "likes(assel, limonade)",
        "food_type(gouda, cheese)",
        "food_type(ritz, cracker)",
        "food_type(steak, meat)",
        "food_type(sausage, meat)",
        "food_type(limonade, juice)",
        "food_type(cookie, dessert)",
        "flavor(sweet, dessert)",
        "flavor(savory, meat)",
        "flavor(savory, cheese)",
        "flavor(sweet, juice)",
        "food_flavor(X, Y) :- food_type(X, Z), flavor(Y, Z)",
        "dish_to_like(X, Y) :- likes(X, L), food_type(L, T), flavor(F, T), food_flavor(Y, F)"])
print("\nKB after filling:")
pprint(new_kb.db)
print("\nlength: ", len(new_kb.db))

# KB before filling:
# Knowledge Base: flavor
# {}
# 
# KB after filling:
# {'dish_to_like': {'facts': [dish_to_like(X,Y):-likes(X,L),food_type(L,T),flavor(F,T),food_flavor(Y,F)],
#                   'goals': [[Goal = likes(X,L), parent = None,
#                              Goal = food_type(L,T), parent = None,
#                              Goal = flavor(F,T), parent = None,
#                              Goal = food_flavor(Y,F), parent = None]],
#                   'terms': [['X', 'Y', 'L', 'T', 'F']]},
#  'flavor': {'facts': [flavor(sweet,dessert),
#                       flavor(savory,meat),
#                       flavor(savory,cheese),
#                       flavor(sweet,juice)],
#             'goals': [[], [], [], []],
#             'terms': [['sweet', 'dessert'],
#                       ['savory', 'meat'],
#                       ['savory', 'cheese'],
#                       ['sweet', 'juice']]},
#  'food_flavor': {'facts': [food_flavor(X,Y):-food_type(X,Z),flavor(Y,Z)],
#                  'goals': [[Goal = food_type(X,Z), parent = None,
#                             Goal = flavor(Y,Z), parent = None]],
#                  'terms': [['X', 'Y', 'Z']]},
#  'food_type': {'facts': [food_type(gouda,cheese),
#                          food_type(ritz,cracker),
#                          food_type(steak,meat),
#                          food_type(sausage,meat),
#                          food_type(limonade,juice),
#                          food_type(cookie,dessert)],
#                'goals': [[], [], [], [], [], []],
#                'terms': [['gouda', 'cheese'],
#                          ['ritz', 'cracker'],
#                          ['steak', 'meat'],
#                          ['sausage', 'meat'],
#                          ['limonade', 'juice'],
#                          ['cookie', 'dessert']]},
#  'likes': {'facts': [likes(noor,sausage),
#                      likes(melissa,pasta),
#                      likes(dmitry,cookie),
#                      likes(nikita,sausage),
#                      likes(assel,limonade)],
#            'goals': [[], [], [], [], []],
#            'terms': [['noor', 'sausage'],
#                      ['melissa', 'pasta'],
#                      ['dmitry', 'cookie'],
#                      ['nikita', 'sausage'],
#                      ['assel', 'limonade']]}}
# 
# length:  5
```

Let’s do some queries in this database using its facts and rules.

``` python
new_kb.query(pl.pl_expr("likes(noor, sausage)"))
# ['Yes']
```

``` python
new_kb.query(pl.pl_expr("likes(noor, pasta)"))
# ['No']
```

I added **Memoization** to speed up the queries.

###### Wikipedia definition: In computing, memoization or memoisation is an optimization technique used primarily to speed up computer programs by storing the results of expensive function calls and returning the cached result when the same inputs occur again.

Let’s test it doing the same query twice and compare time used to do the
query.

``` python
# query 1
from time import time
start = time()
print(new_kb.query(pl.pl_expr("food_flavor(What, sweet)")))
print(time() - start)

# [{'What': 'limonade'}, {'What': 'cookie'}]
# 0.0020236968994140625
```

``` python
# query 2
from time import time
start = time()
print(new_kb.query(pl.pl_expr("food_flavor(Food, sweet)")))
print(time() - start)

# [{'Food': 'limonade'}, {'Food': 'cookie'}]
# 0.0
```

As you see, it took almost no time to return the same answer again and
it also takes care of different Uppercased variable inputs as they
anyways will be the same result no matter what they are.

More Queries:

``` python
new_kb.query(pl.pl_expr("food_flavor(Food, Flavor)"))

# [{'Food': 'gouda', 'Flavor': 'savory'},
#  {'Food': 'steak', 'Flavor': 'savory'},
#  {'Food': 'sausage', 'Flavor': 'savory'},
#  {'Food': 'limonade', 'Flavor': 'sweet'},
#  {'Food': 'cookie', 'Flavor': 'sweet'}]
```

Now we will use the **dish\_to\_like** rule to recommend dishes to
persons based on taste preferences.

``` python
start = time()
print(new_kb.query(pl.pl_expr("dish_to_like(noor, What)")))
print(time() - start)

# [{'What': 'gouda'}, {'What': 'steak'}, {'What': 'sausage'}]
# 0.001992940902709961
```

Let’s test the Memoization again:

``` python
start = time()
print(new_kb.query(pl.pl_expr("dish_to_like(noor, What)")))
print(time() - start)

# [{'What': 'gouda'}, {'What': 'steak'}, {'What': 'sausage'}]
# 0.0
```

##### City Coloring problem

![](pytholog_files/figure-gfm/city_color.png)

###### Image Source: “Seven Languages in Seven Weeks” book.

The problem is **Constraint Satisfaction Problem**. The problem is to
color each city using only three colors but no adjacent cities can be
colored the same. The problem might seem so easy but it’s really
challenging how to tell this to a machine. But using prolog logic it is
kind of easier because all you have to do is to specify the rules of the
problem and prolog will answer.

``` python
## new knowledge base object
city_color = pl.knowledge_base("city_color")
city_color([
    ## facts that red, green and blue are different from each others
    "different(red, green)",
    "different(red, blue)",
    "different(green, red)", 
    "different(green, blue)",
    "different(blue, red)", 
    "different(blue, green)",
    ## rule that the five cities should be with different colors
    """coloring(A, M, G, T, F) :- different(M, T),
    different(M, A),
    different(A, T),
    different(A, M),
    different(A, G),
    different(A, F),
    different(G, F),
    different(G, T)"""
])
```

Let’s query the answer:

``` python
## we will use [0] to return only one answer 
## as prolog will give all possible combinations and answers
city_color.query(pl.pl_expr("coloring(Alabama, Mississippi, Georgia, Tennessee, Florida)"))[0]

# {'Alabama': 'blue',
#  'Mississippi': 'red',
#  'Georgia': 'red',
#  'Tennessee': 'green',
#  'Florida': 'green'}
```

Future implementation will try to come up with ideas to combine this
technique with **machine learning algorithms and neural networks**

**Contribution, ideas and any kind of help will be much appreciated**
