import sys
import numpy as np
import re

equations = []
variables = {}
right_side = []
variable_index = 0

r = re.compile(r"(\d*)([a-z])")

for eq in open(sys.argv[1], 'r'):
    ss = eq.split(' ')
    d = {}
    negative = False
    result = False
    for s in ss:
        if result:
            right_side.append(int(s))
            break
        m = r.match(s)
        if m is None:
            if s == "=": 
                result = True
            elif s == "-":
                negative = True
            elif not s == "+":
                raise ValueError("Unknown symbol")
        else:
            c = int(m.group(1)) if m.group(1) else 1
            v = m.group(2)
            if negative:
                c = -c
                negative = False
            d[v] = int(c)
            if v not in variables:
                variables[v] = variable_index
                variable_index += 1
    equations.append(d)

lin_system = []

for eq in equations:
    l = np.zeros(len(variables))
    for v,c in eq.items():
        l[variables[v]] = c
    lin_system.append(l)


var_names = [i[0] for i in sorted(variables.items(), key=lambda kv: kv[1])]
matrix = np.array(lin_system)
results = np.array(right_side)
augm_matrix = np.array(np.c_[matrix, results])
rank_coef = np.linalg.matrix_rank(matrix)
rank_augm = np.linalg.matrix_rank(augm_matrix)
num_of_variables = variable_index

if rank_coef != rank_augm:
    print("no solution")
elif rank_coef < num_of_variables:
    print("solution space dimension: " + str(num_of_variables - rank_coef))
else:
    r = np.linalg.solve(matrix, results)
    s = "solution: "
    solutions = {}
    for i in range(len(r)):
        solutions[var_names[i]] = str(round(r[i], 10))
    solutions_in_order = sorted(solutions.items())
    for i, sol in enumerate(solutions_in_order):
        s += sol[0] + " = " + sol[1]
        if i < len(solutions_in_order) - 1:
            s += ", "
    print(s)
