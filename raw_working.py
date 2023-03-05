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

def initial_final_constraints(solver, vars, n):
    # Add the final constraint
    for i in range(n):
        for j in range(n):
            solver.add(vars["v{}{}{}".format(i, j,T)] == n*i + j +1)

    # Add the initial constraint
    for i in range(n):
        for j in range(n):
            solver.add(Int("v{}{}{}".format(i,j,0)) == matrix[i][j])
    
# Add the constraints for shifts
def add_shift_constraints(solver, variables, n, t):
    
    clause =  [[[None for _ in range(t)] for _ in range(n)] for _ in range(4)]
    for k in range(1,t+1):
        # Add right shift constraints for rows
        for i in range(n):
                # Roll-over shift for row i
                roll_over_clause = [variables["v{}{}{}".format(i, j, k)] == variables["v{}{}{}".format(i, j-1, k-1)] for j in range(1, n)]
                roll_over_clause.append(variables["v{}0{}".format(i, k)] == variables["v{}{}{}".format(i, n-1, k-1)])
                others = [variables["v{}{}{}".format(l, j, k)] == variables["v{}{}{}".format(l, j, k-1)] for l in range(n) for j in range(n) if l!= i]
                clause[0][i][k-1] = And(roll_over_clause + others)

        # Add left shift constraints for rows
        for i in range(n):
                # Roll-over shift for row i
                roll_over_clause = [variables["v{}{}{}".format(i, j-1, k)] == variables["v{}{}{}".format(i, j, k-1)] for j in range(1, n)]
                roll_over_clause.append(variables["v{}{}{}".format(i, n-1,k)] == variables["v{}{}{}".format(i, 0, k-1)])
                others = [variables["v{}{}{}".format(l, j, k)] == variables["v{}{}{}".format(l, j, k-1)] for l in range(n) for j in range(n) if l!= i]
                clause[1][i][k-1]= And(roll_over_clause + others)

        # Add Down shift constraints for columns
        for j in range(n):
                # Roll-over shift for column j
                roll_over_clause = [variables["v{}{}{}".format(i, j, k)] == variables["v{}{}{}".format(i-1, j, k-1)] for i in range(1, n)]
                roll_over_clause.append(variables["v0{}{}".format(j, k)] == variables["v{}{}{}".format(n-1, j, k-1)])
                others = [variables["v{}{}{}".format(i, l, k)] == variables["v{}{}{}".format(i, l, k-1)] for i in range(n) for l in range(n) if l!= j]
                clause[2][j][k-1] = And(roll_over_clause + others)

        # Add Up shift constraints for columns
        for j in range(n):
                # Roll-over shift for column j
                roll_over_clause = [variables["v{}{}{}".format(i-1, j, k)] == variables["v{}{}{}".format(i, j, k-1)] for i in range(1, n)]
                roll_over_clause.append(variables["v{}{}{}".format(n-1,j, k)] == variables["v{}{}{}".format(0, j, k-1)])
                others = [variables["v{}{}{}".format(i, l, k)] == variables["v{}{}{}".format(i, l, k-1)] for i in range(n) for l in range(n) if l!= j]
                clause[3][j][k-1] = And(roll_over_clause + others)
    
        equal_bools = [] 
        # Add the constraint that the configuration is same as the previous step
        for i in range(n):
            for j in range(n):
                equal_bools.append(variables["v{}{}{}".format(i,j,k)] == variables["v{}{}{}".format(i, j, k-1)])
        
        prev_state_clause = And(equal_bools)

        solver.add(Or(Or([clause[i//n][i%n][k-1] for i in range(4*n)]),prev_state_clause))
    return clause    

vars = initialize_variables(n,T)

s = Solver()

initial_final_constraints(s,vars,n)

assignments = add_shift_constraints(s,vars,n,T)

x = s.check()

if x == sat:
  m = s.model()
  print("sat")
  for k in range(1,T+1):
       for j in range(n):
           if m.eval(assignments[0][j][k-1]):
               print("{}r".format(j))
               break
           if m.eval(assignments[1][j][k-1]):
               print("{}l".format(j))
               break
           if m.eval(assignments[2][j][k-1]):
               print("{}d".format(j))
               break
           if m.eval(assignments[3][j][k-1]):
               print("{}u".format(j))
               break
else: 
  print("unsat")
        