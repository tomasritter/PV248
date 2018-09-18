import sys

to_match = "";
if sys.argv[2] == "composer":
    to_match = "Composer:"
else if sys.argv[2] = "century":
    to_match = "Publication Year:" 
else if sys.argv[2] = "cminor":
    to_match = "Key:"

dict = {}
for line in open(sys.argv[1], 'r'):
    r = re.compile(r"(.*):(.*)\n");
    m = r.match(to_match)
    if m is None:
        continue
    if not key in dict:
        dict[key] = 1
    else:
        dict[key] += 1
    
