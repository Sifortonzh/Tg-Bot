import json, os

VISITOR_FILE = "known_visitors.json"

def is_known(uid):
    if not os.path.exists(VISITOR_FILE): return False
    with open(VISITOR_FILE, "r") as f:
        known = json.load(f)
    return str(uid) in known

def save_visitor(uid):
    if os.path.exists(VISITOR_FILE):
        with open(VISITOR_FILE, "r") as f:
            known = json.load(f)
    else:
        known = {}
    known[str(uid)] = True
    with open(VISITOR_FILE, "w") as f:
        json.dump(known, f)
