import pytholog as pl
import sys
import argparse
import re
from pprint import pprint
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["DEBUG"] = True


def main():
    parser = argparse.ArgumentParser(
        description="pytholog executable tool: prolog experience at command line and a logic knowledge base with no dependencies")
    parser.add_argument("-c", "--consult", help="read an existing prolog file/knowledge base",
                        type=str, required=False)
    parser.add_argument("-n", "--name", help="knowledge base name",
                        type=str, required=True)
    parser.add_argument("-i", "--interactive", help="start an interactive prolog-like session",
                        action="store_true", default=False)
    parser.add_argument("-a", "--api", help="start a flask api",
                        action="store_true", default=True)
    args, _ = parser.parse_known_args()
    args = vars(args)

    name = args["name"]
    kb = pl.KnowledgeBase(name)

    if args["consult"]:
        kb.from_file(args["consult"])
        
    if args["interactive"]:
        type = "interactive"
    else:
        type = "api"

    #run(kb)
    return kb, type


def save_to_file(kb):
    output = kb.name + ".pl"
    with open(output, "w") as o:
        for k in kb.db.keys():
            for f in kb.db[k]["facts"]:
                o.write(f.to_string() + "." + "\n")

    o.close()
    return ("KnowledgeBase is saved into %s file" % output)


def save_quit(kb, exit = True):
    s = save_to_file(kb)
    if exit:
        print(s)
        sys.exit(0)
    else:
        return s


def show_kb(kb):
    for k in kb.db.keys():
        pprint(kb.db[k]["facts"])


def invalid_inpt(kb):
    print("invalid input\n please type 'print' to print the knowledge base\n or 'quit' to save and exit")


def is_fact(inpt):
    if ":-" in inpt: return True
    if "?" in inpt: return False
    s = re.findall(r"(?i)\b[a-z]+\b", inpt)
    return not any(i <= "Z" for i in s)


def _insert(kb, inpt):
    kb([inpt])


def _query(kb, inpt):
    inpt = re.sub("\?", "", inpt)
    cut = (inpt[-1] == "!")
    return kb.query(pl.Expr(inpt[:-1]), cut=cut)


def inpt_prep(inpt):
    return re.sub("\.", "", inpt)

# interactive command line
def run(kb):
    switch = {
        "quit": save_quit,
        "print": show_kb,
    }

    while True:
        sys.stdout.write("?- ")
        sys.stdout.flush()

        inpt = sys.stdin.readline().rstrip("\n")

        if inpt in [" ", ""]: continue

        inpt = inpt_prep(inpt)

        if any(p in inpt for p in "()"):
            if is_fact(inpt):
                _insert(kb, inpt)
                continue
            else:
                pprint(_query(kb, inpt))
                continue

        else:
            switch.get(inpt, invalid_inpt)(kb)
            continue

@app.route("/query", methods=["GET"])
def kb_query():
    inpt = request.args["expr"]
    inpt = inpt_prep(inpt)
    return jsonify(_query(kb, inpt))
    
@app.route("/insert")#, methods=["GET"])
def kb_insert():
    inpt = request.args["expr"]
    input = inpt_prep(inpt)
    _insert(kb, inpt)
    return jsonify("OK")
    
@app.route("/save")#, methods=["GET"])
def kb_save():
    return jsonify(save_quit(kb, exit = False))

if __name__ == "__main__":
    kb, type = main()
    if type == "interactive":
        run(kb)
    else:
        app.run()
