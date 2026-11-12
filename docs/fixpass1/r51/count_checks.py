# Round 51: how many checks a suite actually ran. Usage: count_checks.py <suite name> <suite output>
# report()-style suites: the number of keys in the results object. t_datashape: data blocks checked ("blocks").
# t_hashnames: files checked ("checked"). Prints 0 if nothing parseable was reported.
import sys, json, re
name, t = sys.argv[1], open(sys.argv[2], errors='ignore').read()
m = re.search(r'\{\n.*?\n\}', t, re.S)
try: obj = json.loads(m.group(0)) if m else {}
except Exception: obj = {}
if name == 't_datashape': print(int(obj.get('blocks') or 0))
elif name == 't_hashnames': print(int(obj.get('checked') or 0))
else: print(len(obj))
