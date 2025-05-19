
#set -e
import sys

num_variables = 14
num_clauses = 18

def write_cnf_line(filename, line):
	with open(filename,"r") as f:
		cnffile = f.readlines()
	cnffile.append(line +'\n')
	cnffile[0] = f"p cnf+ {num_variables} {len(cnffile)-1}\n"
	with open(filename,"w") as f:
		for line in cnffile:
			f.write(line)

#import pdb
#pdb.set_trace()
count = 0
#while (count <2):
while (True):
	print(f"round: {count}")
	python gen_card_sat2.py @(num_variables) @(num_clauses)
	cp cnf.cnf cnf_m.cnf
	output1 = ["SAT\n",""]
	iterator = 0
	print("minicard")
	while len(output1)==2 and output1[0]=="SAT\n" and iterator < 2**16:
		print(iterator, end=" ")
		sys.stdout.flush()
		minicard cnf_m.cnf output1.txt -verb=0 > /dev/null 2> /dev/null
		try:
			with open("output1.txt","r") as f:
				output1 = f.readlines()
		except:
			break
		rm output1.txt
		if len(output1)==2 and output1[0]=="SAT\n":
			line = output1[1].strip().split(" ")
			line = " ".join([str(-int(a)) for a in line])
			write_cnf_line("cnf_m.cnf", line)
		iterator += 1
	print("\n")
	count += 1
	cp cnf.cnf cnf_t.cnf
	output2 = ["SAT\n",""]
	iterator = 0
	print("tinicard")
	while len(output2)==2 and output2[0]=="SAT\n" and iterator < 2**16:
		print(iterator, end=" ")
		sys.stdout.flush()
		python tinicardpythonsolver2.py cnf_t.cnf output2.txt  > /dev/null 2> /dev/null
		try:
			with open("output2.txt","r") as f:
				output2 = f.readlines()
		except:
			break
		rm output2.txt
		if len(output2)==2 and output2[0]=="SAT\n":
			line = output2[1].strip().split(" ")
			line = " ".join([str(-int(a)) for a in line])
			write_cnf_line("cnf_t.cnf", line)
		iterator += 1
	print("\n")
	sort cnf_m.cnf > cnf_m.cnfz
	sort cnf_t.cnf > cnf_t.cnfz
	D = $(diff cnf_m.cnfz cnf_t.cnfz)
	if D!='':
		print(D)
		break
