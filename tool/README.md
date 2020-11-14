# Pytholog Tool (Command line & API)

Pytholog tool is an executable tool, built in **python**, that enables **logic programming** and **prolog syntax** 
through **interactive shell** that mimics prolog language and / or **RESTful API** that can be called from other applications.

### The tool is based on the python library pytholog which can be found here: https://github.com/mnoorfawi/pytholog

The tool is made from the Pytholog.py script using **pyinstaller** with the following command:
pyinstaller --noconfirm --onefile --console --hidden-import=pkg_resources.py2_warn --icon "pytholog-logo2.ico"  "Pytholog.py"

The tool starts normally from the command line. Let's look at the arguments that can be specified while initiating the tool:
```bash
$ ./Pytholog -h
usage: Pytholog [-h] [-c CONSULT] -n NAME [-i] [-a]

pytholog executable tool: prolog experience at command line and a logic knowledge base with no dependencies

optional arguments:
  -h, --help            show this help message and exit
  -c CONSULT, --consult CONSULT
                        read an existing prolog file/knowledge base
  -n NAME, --name NAME  knowledge base name
  -i, --interactive     start an interactive prolog-like session
  -a, --api             start a flask api
```

As we can see, we have 4 parameters: **-n --name** which is the only required parameter that is used to give a name to the session,
**-c --consult** which can be used in case we have a pre-existing knowledge base, **-i --interactive** to start an interactive prolog-like session and 
**-a --api** that starts a **RESTful API** written in python/flask.
By default it starts the API.

Let's now try the tool with the accompanied dummy knowledge base
#### First, the interactive shell
```bash
$ ./Pytholog -c dummy.txt -n dummy -i

facts and rules have been added to dummy.db
?- prin
invalid input
 please type 'print' to print the knowledge base
 or 'quit' to save and exit
?- print
[likes(assel,limonade), likes(dmitry,cookie), likes(melissa,pasta), likes(nikita,sausage), likes(noor,sausage)]
[food_type(cookie,dessert), food_type(gouda,cheese), food_type(limonade,juice), food_type(ritz,cracker), food_type(sausage,meat), food_type(steak,meat)]
[flavor(savory,meat), flavor(savory,cheese), flavor(sweet,dessert), flavor(sweet,juice)]
[food_flavor(X,Y):-food_type(X,Z),flavor(Y,Z)]
?- likes(noor, sausage)?
['Yes']
?- likes(nikita, cheese)?
['No']
?- likes(noor, What)?
[{'What': 'sausage'}]
?- food_flavor(What, sweet)?
[{'What': 'cookie'}, {'What': 'limonade'}]
?- dish_to_like(X, Y) :- likes(X, L), food_type(L, T), flavor(F, T), food_flavor(Y, F).
?- dish_to_like(noor, What)!
[{'What': 'gouda'}]
?- quit
KnowledgeBase is saved into dummy.pl file
```

Note the usage of **'.'** is optional and **'?'** is required to differentiate between a query and a new fact to be inserted to the knowledge base.
And the **'!'** is used to **cut** and return the first encountered answer.

#### Now the API
```bash
$ ./Pytholog -c dummy.txt -n dummy -a

facts and rules have been added to dummy.db
 * Serving Flask app "Pytholog" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
facts and rules have been added to dummy.db
 * Debugger is active!
 * Debugger PIN: 222-740-882
```

Let's try to call the API from command line, python and R and in the browser
###### Note that spaces can cause some errors

From R
```r
library(httr)
library(jsonlite)

GET("http://127.0.0.1:5000/query?expr=food_flavor(What,savory)")

# Response [http://127.0.0.1:5000/query?expr=food_flavor(What,savory)]
#   Date: 2020-11-13 19:26
#   Status: 200
#   Content-Type: application/json
#   Size: 94 B
# [
#   {
#     "What": "gouda"
#   }, 
#   {
#     "What": "sausage"
#   }, 
#   {
#     "What": "steak"
#   }
# ...
```

From Command line

```bash
$ curl -s -X POST "http://127.0.0.1:5000/insert?expr=dish_to_like(X,Y):-likes(X,L),food_type(L,T),flavor(F,T),food_flavor(Y,F)"
"OK"
``` 

From python
```python
import json
import requests

url = "http://127.0.0.1:5000/query?expr=dish_to_like(noor,What)!"
r = requests.get(url)

d = json.loads(r.content)
d

# [{'What': 'gouda'}]
```

From **browser** put this into the browser
http://127.0.0.1:5000/save and it will give you **"KnowledgeBase is saved into dummy.pl file"**
and a dummy.pl file will be created.
