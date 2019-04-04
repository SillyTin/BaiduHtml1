from binaryninja import *
import os

def findpath_cg(start, cg, path, pre = None):

	if start not in path.keys():
		path[start] = []
	
	if pre:
		for repath in path[pre]:
			flag = True
			for edge in path[start]:
				if repath == edge[:-1]:
					flag = False
			if flag:
				path[start].append(repath.copy())
			for edge in path[start]:
				if edge[-1] != start:
					edge.append(start)
	else:
		path[start].append([start])

	list = cg[start]
	for item in list:
		findpath_cg(item, cg, path, start)


def findpath_cfg(start, end, cfg_sin, cfg_path_sin, pre = None):

	# cfg_sin: intro procedure, is a dirc
	# cfg_path_sin:{node:[[path1],[path2]]}, intro procedure

	#traverse the basic blocks in the start_func to find a path to the end_func


	if start not in cfg_path_sin.keys():
		cfg_path_sin[start] = []
	
	if pre:
		for repath in cfg_path_sin[pre]:
			flag = True
			for edge in cfg_path_sin[start]:
				if repath == edge[:-1]:
					flag = False
			if flag:
				cfg_path_sin[start].append(repath.copy())
			for edge in cfg_path_sin[start]:
				if edge[-1] != start:
					edge.append(start)
	else:
		cfg_path_sin[start].append([start])

	list = cfg_sin[start]
	for item in list:
		findpath_cfg(item, end, cfg_sin, cfg_path_sin, start)
		print("findpath_cfg_2\n")

	print(cfg_path_sin)

	# for bb in start_func:
		# find the way



if __name__ == '__main__':

	# Load binary file
	path = "/home/wdd/Netgear/httpd"
	bv = BinaryViewType['ELF'].get_view_of_file(path)
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
			# if str(inst[0][0] == 'b'):
			# 	des = str(inst[0][-1])

	for caller in cg.keys():
		if cg[caller] != []:
			for callee in cg[caller]:
				f.write("%s -> %s\n" % (caller , callee))
	f.close()

	# Create CFG
	f = open("%scfg.txt" % (path) , "w")
	cfg = {}
	for func in bv.functions:
		func_name = str(hex(int(func.start)))
		cfg[func_name] = {}
		for bb in func.basic_blocks:
			caller = str(hex(int(bb.start)))
			cfg[func_name][caller] = []
			for edge in bb.outgoing_edges:
				callee = str(hex(int(edge.target.start)))
				if callee not in cfg[func_name][caller]:
					cfg[func_name][caller].append(callee)
	for func in cfg.keys():
		flag = False
		for item in cfg[func]:
			if cfg[func][item] != []:
				flag = True
		if flag:
			f.write("%s:\n" % (func))
			for caller in cfg[func]:
				if cfg[func][caller] != []:
					for callee in cfg[func][caller]:
						f.write("%s -> %s\n" % (caller , callee))
	f.close()

	# Find path in func level
	f = open("%scg_path.txt" % (path) , "w")
	edge = {}
	start = '0x100a0'
	end = '0xd69c'
	findpath_cg(start, cg, edge)
	for i in edge[end]:
		for j in i[:-1]:
			f.write("%s -> " % (j))
		f.write("%s\n" % (i[-1]))
	f.close()

	#Find path in bb level
	f = open("%scfg_path.txt" % (path) , "w")
	cfg_path = {}
	func_path = edge[end]
	for item in func_path:
		start = item[0]
		cfg_path[start] = {}
		end = item[1]
		item = item[1:]
		findpath_cfg(start, end, cfg[start], cfg_path[start])
		print("findpath_cfg_1\n")
		
	f.close()