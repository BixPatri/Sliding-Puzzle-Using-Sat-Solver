### TEAM MEMBERS
## MEMBER 1: 210050009
## MEMBER 2: 210050015
## MEMBER 3: 210050026


from z3 import *
import sys

file = sys.argv[1]

with open(file) as f:
	n,T = [int(x) for x in next(f).split()]
	matrix = []
	for line in f:
		matrix.append([int(x) for x in line.split()])

s = Solver()

# Set s to the required formula

x = s.check()
print(x)
if x == sat:
	m = s.model()
	
	# Output the moves