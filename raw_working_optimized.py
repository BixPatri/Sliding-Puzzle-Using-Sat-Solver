from z3 import *
import math
import sys

file = sys.argv[1]
print
with open(file) as f:
	n,T = [int(x) for x in next(f).split()]
	matrix = []
	for line in f:
		matrix.append([int(x) for x in line.split()])
# print(matrix)


def equal(a,b):
    k=[elem1==elem2 for elem1, elem2 in zip(a, b)]
    return And(k)

# Initialising the list of variables present.
def initialize_variables(n, t):
    # Create variables
    n_b=math.ceil(2*math.log(n,2))
    # variables =  [[[None for _ in range(t+1)] for _ in range(n)] for _ in range(n)]

    variables=[[[[Bool("v[{}][{}][{}][{}]".format(i, j, k,l)) for l in range(n_b)] for k in range(t+1)] for j in range(n)] for i in range(n)]
                    

    # print(variables)
    return variables

# Add constraints for initial and final states
def initial_final_constraints(solver, vars, n):
    n_b=math.ceil(2*math.log(n,2))
    
    # Add the final constraint
    for i in range(n):
        for j in range(n):
            k=n*i+j+1
            for l in range(n_b):
                if k%2:
                    solver.add(vars[i][j][T][l])
                else:
                    solver.add(Not(vars[i][j][T][l]))
                k=k//2
            
    # Add the initial constraint
    for i in range(n):
        for j in range(n):
            k=matrix[i][j]
            for l in range(n_b):
                if k%2:
                    solver.add(vars[i][j][0][l])
                else:
                    solver.add(Not(vars[i][j][0][l]))
                k=k//2
    
# Add the constraints for shifts
def add_shift_constraints(solver, variables, n, t):
    
    # Clauses corresponding to the shifts
    clause =  [[[None for _ in range(t)] for _ in range(n)] for _ in range(4)]

    for k in range(1,t+1):

        # Add right shift constraints for rows
        for i in range(n):
                # Roll-over shift for row i
                roll_over_clause = [equal(variables[i][j][k] ,variables[i][ j-1 ][k-1]) for j in range(1, n)]
                roll_over_clause.append(equal(variables[i][0][k], variables[i][n-1][k-1]))
                others = [equal(variables[l][ j][ k],variables[l][ j][ k-1]) for l in range(n) for j in range(n) if l!= i]
                clause[0][i][k-1] = And(roll_over_clause + others)

        # Add left shift constraints for rows
        for i in range(n):
                # Roll-over shift for row i
                roll_over_clause = [equal(variables[i][j-1][ k], variables[i][j][k-1]) for j in range(1, n)]
                roll_over_clause.append(equal(variables[i][ n-1][k] ,variables[i][0][k-1]))
                others = [equal(variables[l][ j][ k] , variables[l][j][ k-1]) for l in range(n) for j in range(n) if l!= i]
                clause[1][i][k-1]= And(roll_over_clause + others)

        # Add Down shift constraints for columns
        for j in range(n):
                # Roll-over shift for column j
                roll_over_clause = [equal(variables[i][j][k] , variables[i-1][j][ k-1]) for i in range(1, n)]
                roll_over_clause.append(equal(variables[0][j][k] , variables[n-1][ j][ k-1]))
                others = [equal(variables[i][l][k] , variables[i][l][k-1]) for i in range(n) for l in range(n) if l!= j]
                clause[2][j][k-1] = And(roll_over_clause + others)

        # Add Up shift constraints for columns
        for j in range(n):
                # Roll-over shift for column j
                roll_over_clause = [equal(variables[i-1][j][k] ,variables[i] [j] [k-1]) for i in range(1, n)]
                roll_over_clause.append(equal(variables[n-1][j][k] , variables[0][j][k-1]))
                others = [equal(variables[i][l][k] , variables[i][l][k-1]) for i in range(n) for l in range(n) if l!= j]
                clause[3][j][k-1] = And(roll_over_clause + others)
        
        # boolean list to check whether the previous entry same as the current
        equal_bools = [] 

        # Add the constraint that the configuration is same as the previous step
        for i in range(n):
            for j in range(n):
                equal_bools.append(equal(variables[i][j][k],variables[i][j][k-1]))
        
        # Clause that the previous state is exactly same as current
        prev_state_clause = And(equal_bools)

        # Clause that either a move happens or it is same as the current state.
        solver.add(Or(Or([clause[i//n][i%n][k-1] for i in range(4*n)]),prev_state_clause))
    
    # Adding the clause to remove the redundant steps
    for k in range(1,t):
            solver.add(And([Or(Not(clause[0][i][k-1]),Not(clause[1][i][k])) for i in range(n)]))
            solver.add(And([Or(Not(clause[1][i][k-1]),Not(clause[0][i][k])) for i in range(n)]))
            solver.add(And([Or(Not(clause[2][i][k-1]),Not(clause[3][i][k])) for i in range(n)]))
            solver.add(And([Or(Not(clause[3][i][k-1]),Not(clause[2][i][k])) for i in range(n)]))
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