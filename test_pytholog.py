import pytholog as pl

def test_dishes():
    food_kb = pl.knowledge_base("food")
    food_kb(["likes(noor, sausage)",
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
    assert food_kb.query(pl.pl_expr("likes(noor, sausage)"))
    assert food_kb.query(pl.pl_expr("food_flavor(What, sweet)"))
    assert food_kb.query(pl.pl_expr("dish_to_like(noor, What)"))
    
def test_friends():
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
        "has_lot_work(david, 0.3)"])
    assert friends_kb.query(pl.pl_expr("influences(X, rebecca, P)"))
    assert friends_kb.query(pl.pl_expr("smokes(Who)"))
    assert friends_kb.query(pl.pl_expr("to_smoke(Who, P)"))
    assert friends_kb.query(pl.pl_expr("to_have_asthma(Who, P)"))
    
def test_iris():
    iris_kb = pl.knowledge_base("iris")
    iris_kb(["species(setosa, Truth) :- petal_width(W), Truth is W <= 0.80", 
             "species(versicolor, Truth) :- petal_width(W), petal_length(L), Truth is W > 0.80 and L <= 4.95",
             "species(virginica, Truth) :- petal_width(W), petal_length(L), Truth is W > 0.80 and L > 4.95",
             "petal_length(5.1)",
             "petal_width(2.4)"])
    assert iris_kb.query(pl.pl_expr("species(Class, Truth)"))         

