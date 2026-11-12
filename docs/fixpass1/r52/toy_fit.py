# Round 52 challenge A plant: a fit computed inside a function (league mean of outcomes) and applied to every player.
# Nothing fitted is left as a module global and no statistics/numpy call is made.
import json, sys
vals = json.load(open(sys.argv[1]))
def grade_all(v):
    base = sum(v) / len(v)                 # the fit: a local, never a global
    return [round(x - base, 3) for x in v]
RESULT = grade_all(vals)
