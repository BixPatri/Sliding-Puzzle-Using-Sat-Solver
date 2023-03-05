import subprocess
import os
import sys
import time

# test sat and unsat for n in range [1,n_range] and T in range [0,t_range]
# arguement is the file to be tested 
t_range = 5
n_range = 5

testfile = sys.argv[1]

with open('test_output.txt', 'w') as w:
    w.write("")

for i in range(1,n_range+1):
    for j in range(t_range+1):
        data, temp = os.pipe()
        os.write(temp, bytes("5 10\n", "utf-8"));
        os.close(temp)
        s1 = subprocess.check_output("python3 generator.py " + str(i) + " " + str(j) + " sat test.txt > correct.txt", stdin = data, shell = True)
        s2 = subprocess.check_output("python3 " + testfile + " test.txt > my.txt", stdin = data, shell = True)
        s3 = subprocess.check_output("python3 verifier.py test.txt my.txt", stdin = data, shell = True)
        time = s2.decode("utf-8")
        verification = s3.decode("utf-8")
        with open('test_output.txt', 'a') as op:
            op.write('#################################################################################')
            op.write("TEST FOR sat n = " + str(i) + " T = " + str(j) + "\n")
            op.write(time)
            op.write('\n')
            op.write(verification)
            op.write('\n')
            op.write('#################################################################################')
            op.write('\n')
        s4 = subprocess.check_output("python3 generator.py " + str(i) + " " + str(j) + " unsat test.txt > correct.txt", stdin = data, shell = True)
        s5 = subprocess.check_output("python3 " + testfile + " test.txt", stdin = data, shell = True)
        unsat = s5.decode("utf-8")
        with open('test_output' +'.txt', 'a') as op:
            op.write('*********************************************************************************')
            op.write("TEST FOR unsat n = " + str(i) + " T = " + str(j) + "\n")
            if unsat != "unsat\n":
                op.write("INCORRECT\n")
            op.write(unsat)
            op.write('\n')
            op.write('*********************************************************************************')
            op.write('\n')
            
            