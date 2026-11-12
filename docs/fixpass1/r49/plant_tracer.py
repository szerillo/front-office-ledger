# Round 49 plant for the I1 tracer: an engine row spelled "Jesus Luzardo" must trace to the player file "Jesús Luzardo",
# and an unrelated name must not. Runs only the evaluator's traced() on stub data. Usage: python3 plant_tracer.py <evaluator.py>
import sys, json, re
src = open(sys.argv[1]).read()
a = src.find('import unicodedata\ndef fold') if 'def fold' in src else src.find('def traced'); b = src.find('unl = ')
ns = {'json': json, 're': re, 'NAMES': {666200: 'Jesús Luzardo'}, 'CH': {666200}, 'CHs': {'666200'},
      'RB': {'phi': {'allx_ext': [["2026-03-15", "Extended Jesus Luzardo · 5 yr / $135.0M (veteran)", 2.1]]},
             'nyy': {'allx_ext': [["2008-03-15", "Extended Derek Jeter · 10 yr / $189.0M (veteran)", 1.0]]}}}
exec(src[a:b].split('# 4:')[0].split('unl =')[0], ns)
plants = {'accent_folded_traces': ns['traced']('phi', 'ext') is True, 'unrelated_not_traced': ns['traced']('nyy', 'ext') is False}
print(json.dumps(plants)); sys.exit(0 if all(plants.values()) else 1)
