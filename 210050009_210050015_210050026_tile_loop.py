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
            for k in range(t+1):
                var_name = "v{}{}{}".format(i, j, k)
                variables[var_name] = Int(var_name)

    return variables

vars = initialize_variables(n,T)
s = Solver()

for i in range(n):
        for j in range(n):
            s.add(vars["v{}{}{}".format(i, j,T)] == n*i + j +1)

for i in range(n):
        for j in range(n):
	        s.add(Int("v{}{}{}".format(i,j,0)) == matrix[i][j])
    
     
def add_shift_constraints(solver, variables, n, t):
    for k in range(1,t+1):
        # Add right shift constraints for rows
        clause = []
        for i in range(n):
                # Roll-over shift for row i
                roll_over_clause = [variables["v{}{}{}".format(i, j, k)] == variables["v{}{}{}".format(i, j-1, k-1)] for j in range(1, n)]
                roll_over_clause.append(variables["v{}0{}".format(i, k)] == variables["v{}{}{}".format(i, n-1, k-1)])
                clause.append(And(roll_over_clause))

        # Add left shift constraints for rows
        for i in range(n):
                # Roll-over shift for row i
                roll_over_clause = [variables["v{}{}{}".format(i, j-1, k)] == variables["v{}{}{}".format(i, j, k-1)] for j in range(1, n)]
                roll_over_clause.append(variables["v{}{}{}".format(i, n-1,k)] == variables["v{}{}{}".format(i, 0, k-1)])
                clause.append(And(roll_over_clause))

        # Add Down shift constraints for columns
        for j in range(n):
                # Roll-over shift for column j
                roll_over_clause = [variables["v{}{}{}".format(i, j, k)] == variables["v{}{}{}".format(i-1, j, k-1)] for i in range(1, n)]
                roll_over_clause.append(variables["v0{}{}".format(j, k)] == variables["v{}{}{}".format(n-1, j, k-1)])
                clause.append(And(roll_over_clause))

        # Add Up shift constraints for columns
        for j in range(n):
                # Roll-over shift for column j
                roll_over_clause = [variables["v{}{}{}".format(i-1, j, k)] == variables["v{}{}{}".format(i, j, k-1)] for i in range(1, n)]
                roll_over_clause.append(variables["v{}{}{}".format(n-1,j, k)] == variables["v{}{}{}".format(0, j, k-1)])
                clause.append(And(roll_over_clause))
        
        prev_state_clause = []
        
        # Add the constraint that the row is same as the previous step
        row_shift = []
        for i in range(n):
            curr_row_shift = []
            for j in range(n):
                curr_row_shift.append(variables["v{}{}{}".format(i,j,k)] == variables["v{}{}{}".format(i, j, k-1)])
            row_shift.append(And(curr_row_shift))

        prev_state_clause.append(Sum([z3.If(row_shift[p],0,1) for p in range(n)]) <= 1)
        
        # Add the constraint that the col is same as the previous step
        col_shift = []
        for j in range(n):
            curr_col_shift = []
            for i in range(n):
                curr_col_shift.append(variables["v{}{}{}".format(i,j,k)] == variables["v{}{}{}".format(i, j, k-1)])
            col_shift.append(And(curr_col_shift))

        prev_state_clause.append(Sum([z3.If(col_shift[p],0,1) for p in range(n)]) <= 1)

        # If any row changes then the other rows remain the same same with the columns.
        solver.add(Or(prev_state_clause))

        # Add constraint to ensure Atmost one shift per time step
        solver.add(Sum([z3.If(clause[i], 0, 1) for i in range(4*n)]) <= 1)

add_shift_constraints(s,vars,n,T)
x = s.check()

print(x)
if x == sat:
	m = s.model()
    
print(m)
        