from z3 import *
import sys

file = sys.argv[1]

with open(file) as f:
	n,T = [int(x) for x in next(f).split()]
	matrix = []
	for line in f:
		matrix.append([int(x) for x in line.split()])

## initialising the list of variables present.
def initialize_variables(n, t):
    # Create variables
    variables = {}
    for i in range(n):
        for j in range(n):
            for k in range(t):
                var_name = "v{}{}{}".format(i, j, k)
                variables[var_name] = Int(var_name)

    return variables

vars = initialize_variables(n,T)
s = Solver()

for i in range(n):
        for j in range(n):
            s.add(vars["v{}{}0".format(i, j)] == n*i + j +1)

def add_shift_constraints(solver, variables, n, t):
    # Add right shift constraints for rows
    for i in range(n):
        for k in range(1,t):
            # Roll-over shift for row i
            roll_over_clause = [variables["v{}{}{}".format(i, j, k)] == variables["v{}{}{}".format(i, j-1, k-1)] for j in range(1, n)]
            roll_over_clause.append(variables["v{}0{}".format(i, k)] == variables["v{}{}{}".format(i, n-1, k-1)])
            solver.add(Or(roll_over_clause))

    # Add left shift constraints for rows
    for i in range(n):
        for k in range(1,t):
            # Roll-over shift for row i
            roll_over_clause = [variables["v{}{}{}".format(i, j-1, k)] == variables["v{}{}{}".format(i, j, k-1)] for j in range(1, n-1)]
            roll_over_clause.append(variables["v{}{}{}".format(i, n-1,k)] == variables["v{}{}{}".format(i, 0, k-1)])
            solver.add(Or(roll_over_clause))

    # Add Down shift constraints for columns
    for j in range(n):
        for k in range(1,t):
            # Roll-over shift for column j
            roll_over_clause = [variables["v{}{}{}".format(i, j, k)] == variables["v{}{}{}".format(i-1, j, k-1)] for i in range(1, n)]
            roll_over_clause.append(variables["v0{}{}".format(j, k)] == variables["v{}{}{}".format(n-1, j, k-1)])
            solver.add(Or(roll_over_clause))

    # Add Up shift constraints for columns
    for j in range(n):
        for k in range(1,t):
            # Roll-over shift for column j
            roll_over_clause = [variables["v{}{}{}".format(i-1, j, k)] == variables["v{}{}{}".format(i, j, k-1)] for i in range(1, n)]
            roll_over_clause.append(variables["v{}{}{}".format(n-1,j, k)] == variables["v{}{}{}".format(0, j, k-1)])
            solver.add(Or(roll_over_clause))

    # # Add constraint to ensure exactly one shift per time step
    # shift_vars = [Bool("s{}".format(k)) for k in range(1,t)]
    # shift_clause = []
    # for k in range(1,t):
    #     row_shift_clause = [Or(variables["v{}{}{}".format(i, j, k)] != variables["v{}{}{}".format(i, j-1, k)], j == 0) for i in range(n) for j in range(1, n)]
    #     col_shift_clause = [Or(variables["v{}{}{}".format(i, j, k)] != variables["v{}{}{}".format(i-1, j, k)], i == 0) for i in range(1, n) for j in range(n)]
    #     shift_clause.append(Or(row_shift_clause + col_shift_clause + [shift_vars[k-1]]))
    # solver.add(shift_clause)

    # # Add constraint to ensure at most one shift per time step
    # for k in range(1,t):
    #     shift_clause = [variables["s{}".format(k)] == 0] + [variables["s{}".format(l)] == 0 for l in range(1,t) if l != k]
    #     solver.add(Or(shift_clause))

add_shift_constraints(s,vars,n,T)
x = s.check()

print(x)
if x == sat:
	m = s.model()
    
print(m)
        