#### How friends can influence each other into smoking based on some other factors.

###### The example is inspired by [problog](https://dtai.cs.kuleuven.be/problog/tutorial/basic/05_smokers.html)

Here how we can define the knowledge base in **Prolog**:

```prolog
stress(X, P) :- has_lot_work(X, P2), P is P2 * 0.2.
to_smoke(X, Prob) :- stress(X, P1), friends(Y, X), influences(Y, X, P2), smokes(Y), Prob is P1 * P2.
to_have_asthma(X, 0.4) :- smokes(X).
to_have_asthma(X, Prob) :- to_smoke(X, P2), Prob is P2 * 0.25.
friends(X, Y) :- friend(X, Y).
friends(X, Y) :- friend(Y, X).
influences(X, Y, 0.6) :- friends(X, Y).
friend(peter, david).
friend(peter, rebecca).
friend(daniel, rebecca).
friend(david, david).
smokes(peter).
smokes(rebecca).
has_lot_work(daniel, 0.8).
has_lot_work(david, 0.3).
```

So much similar in **python** with **pytholog**:

```python
friends_kb = pl.knowledge_base("friends")
friends_kb([
    "stress(X, P) :- has_lot_work(X, P2), P is P2 * 0.2",
    "to_smoke(X, Prob) :- stress(X, P1), friends(Y, X), influences(Y, X, P2), smokes(Y), Prob is P1 * P2",
    "to_have_asthma(X, 0.4) :- smokes(X)",
    "to_have_asthma(X, Prob) :- to_smoke(X, P2), Prob is P2 * 0.25",
    "friends(X, Y) :- friend(X, Y)",
    "friends(X, Y) :- friend(Y, X)",
    "influences(X, Y, 0.6) :- friends(X, Y)",
    "friend(peter, david)",
    "friend(peter, rebecca)",
    "friend(daniel, rebecca)",
    "friend(david, david)",
    "smokes(peter)",
    "smokes(rebecca)",
    "has_lot_work(daniel, 0.8)",
    "has_lot_work(david, 0.3)"
])
```

Let's now perform some queries in both languages:
Prolog:

```prolog
influences(X, rebecca, P).
% P = 0.59999999999999998
% X = peter ? ;
% P = 0.59999999999999998
% X = daniel ? ;

smokes(Who).
% Who = peter ? ;
% Who = rebecca ;

to_smoke(Who, P).
% P = 0.096000000000000016
% Who = daniel ? ;
% P = 0.035999999999999997
% Who = david ? ;

to_have_asthma(Who, P).
% P = 0.40000000000000002
% Who = peter ? ;
% P = 0.40000000000000002
% Who = rebecca ? ;
% P = 0.024000000000000004
% Who = daniel ? ;
% P = 0.0089999999999999993
% Who = david ? ;
```

Python:

```python
friends_kb.query(pl.pl_expr("influences(X, rebecca, P)"))
# [{'X': 'peter', 'P': '0.6'}, {'X': 'daniel', 'P': '0.6'}]

friends_kb.query(pl.pl_expr("smokes(Who)"))
# [{'Who': 'peter'}, {'Who': 'rebecca'}]

friends_kb.query(pl.pl_expr("to_smoke(Who, P)"))
# [{'Who': 'daniel', 'P': 0.09600000000000002}, {'Who': 'david', 'P': 0.036}]

friends_kb.query(pl.pl_expr("to_have_asthma(Who, P)"))
# [{'Who': 'peter', 'P': '0.4'},
#  {'Who': 'rebecca', 'P': '0.4'},
#  {'Who': 'daniel', 'P': 0.024000000000000004},
#  {'Who': 'david', 'P': 0.009}]
```

The two languages are performing the same way and giving the same results! :D
This is the purpose of pytholog, to mimic the way prolog behaves inside python.















