from binaryninja import *
import os

if __name__ == '__main__':

	# Load binary file
	path = "/home/wdd/Netgear/httpd"
	bv = BinaryViewType['ELF'].get_view_of_file(path)
	# bv.update_analysis_and_wait()
	print("Analysis %s done" % (path))

	# Create dir
	path = path +'_ninja/'
	isExists=os.path.exists(path)
	if not isExists:
		os.makedirs(path) 
		print(path+' Create dir success')
	else:
		print(path+' already exists')

	# Get functions
	f = open("%sfunc.txt" % (path) , "w")
	funcs = {}
	for func in bv.functions:
		addr = str(hex(int(func.start)))
		funcs[addr] = func.symbol.name
	for addr in funcs.keys():
		f.write("%s : %s\n" % (addr , funcs[addr]))
	f.close()

	# Get instructions
	f = open("%sinst.txt" % (path) , "w")
	inst = []
	for i in bv.instructions:
		ins = ''
		for j in i[0]:
			ins = ins + str(j)
		inst.append("%s : %s" % (str(hex(int(i[1]))), ins))
	for i in inst:
		f.write("%s\n" % (i))
	f.close()

	# Create CG
	f = open("%scg.txt" % (path) , "w")
	cg = {}
	for func in bv.functions:
		caller = str(hex(int(func.start)))
		cg[caller] = []
		for inst in func.instructions:
			if func.is_call_instruction(inst[1]):
				if str(inst[0][-1]).startswith("0x"):
					if str(inst[0][-1]) not in cg[caller]:
						cg[caller].append(str(inst[0][-1]))
	for caller in cg.keys():
		if cg[caller] != []:
			for callee in cg[caller]:
				f.write("%s -> %s\n" % (caller , callee))
	f.close()

	# Create CFG
	f = open("%scfg.txt" % (path) , "w")
	cfg = {}
	for func in bv.functions:
		cfg[func.symbol.name] = {}
		for bb in func.basic_blocks:
			caller = str(hex(int(bb.start)))
			cfg[func.symbol.name][caller] = []
			for edge in bb.outgoing_edges:
				callee = str(hex(int(edge.target.start)))
				if callee not in cfg[func.symbol.name][caller]:
					cfg[func.symbol.name][caller].append(callee)
	for func in cfg.keys():
		f.write("%s:\n" % (func))
		for caller in cfg[func]:
			if cfg[func][caller] != []:
				for callee in cfg[func][caller]:
					f.write("%s -> %s\n" % (caller , callee))
	f.close()