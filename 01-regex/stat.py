import sys
import re

to_match = ""
if sys.argv[2] == "composer":
    to_match = "Composer:"
elif sys.argv[2] == "century":
    to_match = "Publication Year:" 
elif sys.argv[2] == "cminor":
    to_match = "Key: (.*)c"
else:
    exit

dict = {}
for line in open(sys.argv[1], 'r'):
    r = re.compile(r"(.*):(.*)");
    m = r.match(to_match)
    if m is None:
        continue
    s = r.split(r";")
    for key in s:
        if not key in dict:
            dict[key] = 1
        else:
            dict[key] += 1
for k, v in dict:
    print("Key: " + k + " Value: "+ v)

