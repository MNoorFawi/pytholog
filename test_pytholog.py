import pytholog as pl

def test_dishes():
    food_kb = pl.KnowledgeBase("food")
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
    assert food_kb.query(pl.Expr("likes(noor, sausage)")) == ["Yes"]
    answer = {"What": "cookie"}
    query = food_kb.query(pl.Expr("food_flavor(What, sweet)"))
    assert answer in query
    
def test_friends():
    friends_kb = pl.KnowledgeBase("friends")
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
    david = {'Who': 'david', 'P': 0.036}
    assert david in friends_kb.query(pl.Expr("to_smoke(Who, P)"))
    dan_reb = [{'Who': 'rebecca', 'P': '0.4'}, {'Who': 'daniel', 'P': 0.024000000000000004}]
    assert all(i in friends_kb.query(pl.Expr("to_have_asthma(Who, P)")) for i in dan_reb)
    
def test_iris():
    iris_kb = pl.KnowledgeBase("iris")
    iris_kb(["species(setosa, Truth) :- petal_width(W), Truth is W <= 0.80", 
             "species(versicolor, Truth) :- petal_width(W), petal_length(L), Truth is W > 0.80 and L <= 4.95",
             "species(virginica, Truth) :- petal_width(W), petal_length(L), Truth is W > 0.80 and L > 4.95",
             "petal_length(5.1)",
             "petal_width(2.4)"])
    query = iris_kb.query(pl.Expr("species(Class, Truth)"))
    answer = list(filter(lambda d: d['Truth'] == "Yes", query))[0]
    correct_answer = {'Class': 'virginica', 'Truth': 'Yes'}
    assert answer == correct_answer

def test_graph():
    graph = pl.KnowledgeBase("graph")
    graph(["edge(a, b, 6)", "edge(a, c, 1)", "edge(b, e, 4)",
           "edge(b, f, 3)", "edge(c, d, 3)", "edge(d, e, 8)",
           "edge(e, f, 2)",
           "path(X, Y, W) :- edge(X , Y, W)",
           "path(X, Y, W) :- edge(X, Z, W1), path(Z, Y, W2), W is W1 + W2"])

    query = graph.query(pl.Expr("path(a, e, W)"), cut = True)
    assert [d.get("W") for d in query][0] == 10
    
