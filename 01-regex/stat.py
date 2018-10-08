import sys
import re

r = None

# Regular expression to look for
if sys.argv[2] == "composer":
    r = re.compile(r"Composer: (.*)")
elif sys.argv[2] == "century":
    r = re.compile(r"Composition Year: (.*)")
elif sys.argv[2] == "cminor":
    r = re.compile(r"Key: (.*)")
else:
    exit()

dict = {}

for line in open(sys.argv[1], 'r'):
    m = r.match(line)
    if m is None:
        continue

    #split the capture at ;
    s = re.split(r"; ", m.group(1))
    for key in s:
        # Remove everything after '('
        key = key.split("(", 1)[0]
        
        # remove space and ',' from the right, error in dataset
        key = key.rstrip(", ")
        if key is "": 
            continue
        if not key in dict:
            dict[key] = 1
        else:
            dict[key] += 1
            
if sys.argv[2] == "composer":
    for k, v in dict.items():
        print(k + ": " + str(v))
elif sys.argv[2] == "century":
    # items were saved by year
    data = [0] * 21
    for i in range(21):
        data[i] = 0
    for k, v in dict.items():
        # match items only where there is a year
        kk = re.match(r"\d\d\d\d", k)
        if not kk is None:
            data[int(kk.group(0)[0:2])] += v
        kk = re.match(r"(\d\d)th century", k)
        if not kk is None:
            data[int(kk.group(1)) - 1] += v
    for i in range(21):
        if data[i] is 0: 
            continue
        print(str(i + 1) + "th century: " + str(data[i]))
elif sys.argv[2] == "cminor":
    print("Number of songs in c minor: " + str(dict["c"]))

