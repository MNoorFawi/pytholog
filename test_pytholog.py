import pytholog as pl

def test_pl():
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