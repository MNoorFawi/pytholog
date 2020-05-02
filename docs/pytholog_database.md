# Pytholog as a logic database

## Overview

We will use [DVD Rental](https://www.postgresqltutorial.com/postgresql-sample-database/) database to feed a knowledge base
as facts and rules, then logically query the database.

[Here](https://github.com/MNoorFawi/neo4j-and-postgresql-with-R) we can find how to create the database in postgresql and insert the data.

Let's connect to the database in python and see how it looks like:

``` python
import psycopg2
import pandas as pd

psql = psycopg2.connect(host = "localhost", database = "dvdrental",
                      user = "postgres", password = "password")
cursor = psql.cursor()
## fetch some data to confirm connection
pd.read_sql("SELECT * FROM language;", psql)

#    language_id                  name         last_update
# 0            1  English              2006-02-15 10:02:19
# 1            2  Italian              2006-02-15 10:02:19
# 2            3  Japanese             2006-02-15 10:02:19
# 3            4  Mandarin             2006-02-15 10:02:19
# 4            5  French               2006-02-15 10:02:19
# 5            6  German               2006-02-15 10:02:19
```

Let's see what the table names are:

``` python
cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
print(cursor.fetchall())

# [('actor',), ('store',), ('address',), ('category',), ('city',), ('country',), 
# ('customer',), ('film_actor',), ('film_category',), ('inventory',), ('language',), 
# ('rental',), ('staff',), ('payment',), ('film',), ('movies_rental',), ('compressed_movies_rental',)]
```

``` python
def query_defn(table):
    return f"SELECT * FROM {table};"
```

## Reading tables into python

No we will read the tables we will query into python and do some transformation to have values in lowercase.

``` python
actor = pd.read_sql(query_defn("actor"), psql)
actor["Actor"] = (actor["first_name"] + "_" + actor["last_name"]).str.lower()
actor.head()

#    actor_id first_name  ...             last_update                Actor
# 0         1   Penelope  ... 2013-05-26 14:47:57.620     penelope_guiness
# 1         2       Nick  ... 2013-05-26 14:47:57.620        nick_wahlberg
# 2         3         Ed  ... 2013-05-26 14:47:57.620             ed_chase
# 3         4   Jennifer  ... 2013-05-26 14:47:57.620       jennifer_davis
# 4         5     Johnny  ... 2013-05-26 14:47:57.620  johnny_lollobrigida
# [5 rows x 5 columns]
```

``` python
language = pd.read_sql(query_defn("language"), psql)
film = pd.read_sql(query_defn("film"), psql)
category = pd.read_sql(query_defn("category"), psql)
#customer = pd.read_sql(query_defn("customer"), psql)
language["name"] = language["name"].str.lower()
film["title"] = film["title"].str.replace(" ", "_").str.lower()
category["name"] = category["name"].str.lower()
#customer["Customer"] = (customer["first_name"] + "_" + customer["last_name"]).str.lower()
film_category = pd.read_sql(query_defn("film_category"), psql)
#film[film.film_id.isin(film_category[film_category.category_id == 14].film_id)]

print(film.loc[film.film_id == 1, "title"])
# 4    academy_dinosaur
# Name: title, dtype: object

print(actor.head())
#    actor_id first_name  ...             last_update                Actor
# 0         1   Penelope  ... 2013-05-26 14:47:57.620     penelope_guiness
# 1         2       Nick  ... 2013-05-26 14:47:57.620        nick_wahlberg
# 2         3         Ed  ... 2013-05-26 14:47:57.620             ed_chase
# 3         4   Jennifer  ... 2013-05-26 14:47:57.620       jennifer_davis
# 4         5     Johnny  ... 2013-05-26 14:47:57.620  johnny_lollobrigida
```

## Defining Knowledge Base
**Let's initiate the knowledge base and feed it with for loops.**

We will use rules as the query statements and views if we need some joining and conditions.

``` python
import pytholog as pl
dvd = pl.KnowledgeBase("dvd_rental")

for i in range(film.shape[0]):
    dvd([f"film({film.film_id[i]}, {film.title[i]}, {film.language_id[i]})"])

for i in range(language.shape[0]):
    dvd([f"language({language.language_id[i]}, {language.name[i]})"])
    
## simple query	
dvd(["film_language(F, L) :- film(_, F, LID), language(LID, L)"])
dvd.query(pl.Expr("film_language(young_language, L)"))
# [{'L': 'english'}]
```
## Rules as views
### film_category
We will create film_category view

``` python
for i in range(category.shape[0]):
    dvd([f"category({category.category_id[i]}, {category.name[i]})"])
    
for i in range(film_category.shape[0]):
    dvd([f"filmcategory({film_category.film_id[i]}, {film_category.category_id[i]})"])
    
dvd(["film_category(F, C) :- film(FID, F, _), filmcategory(FID, CID), category(CID, C)"]) ## "_" to neglect this term

## another query to see what films in sci-fi category 
dvd.query(pl.Expr("film_category(F, sci-fi)"))

# [{'F': 'annie_identity'},
#  {'F': 'armageddon_lost'},
# .....

#  {'F': 'titans_jerk'},
#  {'F': 'trojan_tomorrow'},
#  {'F': 'unforgiven_zoolander'},
#  {'F': 'vacation_boondock'},
#  {'F': 'weekend_personal'},
#  {'F': 'whisperer_giant'},
#  {'F': 'wonderland_christmas'}]
```
### film_actor
Let's join actors and films

``` python
for i in range(actor.shape[0]):
    dvd([f"actor({actor.actor_id[i]}, {actor.Actor[i]})"])
    
film_actor = pd.read_sql(query_defn("film_actor"), psql)
#print(film_actor[film_actor["actor_id"] == 3].shape)
print(film_actor.shape)
#(5462, 3)
for i in range(film_actor.shape[0]):
    dvd([f"filmactor({film_actor.film_id[i]}, {film_actor.actor_id[i]})"])

dvd(["film_actor(F, A) :- film(FID, F, _), filmactor(FID, AID), actor(AID, A)"])

dvd.query(pl.Expr("film_actor(annie_identity, Actor)"))
#[{'Actor': 'adam_grant'}, {'Actor': 'cate_mcqueen'}, {'Actor': 'greta_keitel'}]

## query actors in a film
dvd.query(pl.Expr("film_actor(academy_dinosaur, Actor)"))
# [{'Actor': 'penelope_guiness'},
#  {'Actor': 'christian_gable'},
#  {'Actor': 'lucille_tracy'},
#  {'Actor': 'sandra_peck'},
#  {'Actor': 'johnny_cage'},
#  {'Actor': 'mena_temple'},
#  {'Actor': 'warren_nolte'},
#  {'Actor': 'oprah_kilmer'},
#  {'Actor': 'rock_dukakis'},
#  {'Actor': 'mary_keitel'}]

### query films that an actor performed in
dvd.query(pl.Expr("film_actor(Film, penelope_guiness)"))
# [{'Film': 'academy_dinosaur'},
#  {'Film': 'anaconda_confessions'},
#  {'Film': 'angels_life'},
#  {'Film': 'bulworth_commandments'},
#  {'Film': 'cheaper_clyde'},
#  {'Film': 'color_philadelphia'},
#  {'Film': 'elephant_trojan'},
#  {'Film': 'gleaming_jawbreaker'},
#  {'Film': 'human_graffiti'},
#  {'Film': 'king_evolution'},
#  {'Film': 'lady_stage'},
#  {'Film': 'language_cowboy'},
#  {'Film': 'mulholland_beast'},
#  {'Film': 'oklahoma_jumanji'},
#  {'Film': 'rules_human'},
#  {'Film': 'splash_gump'},
#  {'Film': 'vertigo_northwest'},
#  {'Film': 'westward_seabiscuit'},
#  {'Film': 'wizard_coldblooded'}]

### simple yes or no query
dvd.query(pl.Expr("film_actor(academy_dinosaur, lucille_tracy)"))
# ['Yes']
```

### actor_category
Actor Category view to see in which categories an actor performed.

```python
dvd(["actor_category(A, C) :- film_actor(F, A), film_category(F, C)"])

jd = dvd.query(pl.Expr("actor_category(jennifer_davis, Category)"))

from pprint import pprint
merged = {}
for d in jd:
    for k, v in d.items():
        if k not in merged: merged[k] = set()
        merged[k].add(v)

pprint(merged)
# {'Category': {'action',
#               'animation',
#               'comedy',
#               'documentary',
#               'drama',
#               'family',
#               'horror',
#               'music',
#               'new',
#               'sci-fi',
#               'sports',
#               'travel'}}
```

## Saving knowledge base to prolog file
Finally, let's now write those facts and rules to a prolog file.

``` python
with open("dvd_rental.pl", "w") as f:
    for i in dvd.db.keys():
        for d in dvd.db[i]["facts"]:
            f.write(d.to_string() + "." + "\n")
    
f.close()
```