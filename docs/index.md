pytholog (Write Prolog in Python)
================

[![Build Status](https://travis-ci.com/MNoorFawi/pytholog.svg?branch=master)](https://travis-ci.com/MNoorFawi/pytholog)

## Overview

Python library that enables using **logic programming** in python. 
The aim of the library is to explore ways to use symbolic reasoning with machine learning.

Pytholog supports probabilities.

Pytholog gives facts indices (first term) and uses **binary search** to search for relevant facts instead of looping over all knowledge base.
So when defining rules, **make sure that the main search terms are in the first position to speed up the search queries.**

OR can be implemented with defining the rules as many times as the OR facts. For example, to say "fly(X) :- bird(X) ; wings(X)." can be defined as two rules as follows: "fly(X) :- bird(X)." and "fly(X) :- wings(X)."


#### prolog syntax
![](/img/prolog_ex.png)

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
