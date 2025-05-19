
#set -e

def write_cnf_line(filename, line):
	with open(filename,"r") as f:
		cnffile = f.readlines()
	cnffile.append(line +'\n')
	cnffile[0] = f"p cnf+ 10 {len(cnffile)-1}\n"
	with open(filename,"w") as f:
		for line in cnffile:
			f.write(line)

#import pdb
#pdb.set_trace()
count = 0
#while (count <50):
while (True):
	print(f"round: {count}")
	python gen_card_sat.py
	cp cnf.cnf cnf_m.cnf
	output1 = ["SAT\n",""]
	iterator = 0
	while len(output1)==2 and output1[0]=="SAT\n" and iterator < 2**11:
		minicard cnf_m.cnf output1.txt
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
	count += 1
	cp cnf.cnf cnf_t.cnf
	output2 = ["SAT\n",""]
	iterator = 0
	while len(output2)==2 and output2[0]=="SAT\n" and iterator < 2**11:
		../tinisat cnf_t.cnf output2.txt
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
	sort cnf_m.cnf > cnf_m.cnfz
	sort cnf_t.cnf > cnf_t.cnfz
	D = $(diff cnf_m.cnfz cnf_t.cnfz)
	if D!='':
		print(D)
		break
