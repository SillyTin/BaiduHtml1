from binaryninja import *
import os

def findpath_cg(start, end, cg, cg_path):

	related_node = [end]
	find_related_node(end, related_node, cg)
	path = []
	dfs(start, end, path, cg_path, cg, related_node)


def findpath_cfg(start, end, cfg_sin, cfg_path_sin):
	# cfg_sin: intro procedure, is a dirc
	# cfg_path_sin:{node->node:[[path1],[path2]]}, intro procedure

	dst_bb = find_dst_bb(start, end)

	for bb in dst_bb:
		dominators = []
		get_dominators(bb, dominators)
		print('dominators')
		for i in range(len(dominators)-1):
			start = hex(int(dominators[i+1].start))
			end = hex(int(dominators[i].start))
			name = "%s->%s" % (start,end)
			cfg_path_sin[name] = []
			# print(name)
			findpath_cg(start, end, cfg_sin, cfg_path_sin[name])
			# print(cfg_path_sin[name])
			i += 1


def find_related_node(end, related_node, graph):
	
	for i in graph.keys():
		if end in graph[i]:
			if i not in related_node:
				related_node.append(i)
				find_related_node(i, related_node, graph)


def get_dominators(bb, dominators):
	# bb is binaryninja basic_block object
	# dominators is a list including dominators of bb

	global bv

	if bb.immediate_dominator:
		bb = bb.immediate_dominator
		dominators.append(bb)
		get_dominators(bb, dominators)


def dfs(start, end, path, all_path, graph, related_node):
	# depth-first-search
	# start and end are strings of hex address in a graph
	# path is a list of node in a tmp path
	# all_path is a list including all paths from start to end
	# related_node is a list including all nodes related to end

	if len(all_path) > 10000:
		return

	if start == end:
		path.append(end)
		all_path.append(path.copy())
		path.pop()
	else:
		path.append(start)
		for i in graph[start]:
			if i not in path and i in related_node:
				dfs(i, end, path, all_path, graph, related_node)

		path.pop()


def find_dst_bb(src, dst):
	# src and dst are strings of hex address such as find_dst_bb('0x100a0', '0x19b3c')
	# dst_bb is a list including the bb will call the dst func

	src_addr = int(src,16)
	function = bv.get_function_at(src_addr)

	dst_bb = []
	for inst in function.instructions:
		if str(inst[0][-1]) == dst:
			dst_addr = int(str(inst[1]))
			dst_bb.append(function.get_basic_block_at(dst_addr))

	return dst_bb


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
	funcs = {}
	for func in bv.functions:
		addr = hex(int(func.start))
		funcs[addr] = func.symbol.name

	f = open("%sfunc.txt" % (path) , "w")
	for addr in funcs.keys():
		f.write("%s : %s\n" % (addr , funcs[addr]))
	f.close()
	print("get func")

	# Get instructions
	inst = []
	for i in bv.instructions:
		ins = ''
		for j in i[0]:
			ins = ins + str(j)
		inst.append("%s : %s" % (hex(int(i[1])), ins))

	f = open("%sinst.txt" % (path) , "w")
	for i in inst:
		f.write("%s\n" % (i))
	f.close()
	print("get inst")

	# Create CG
	cg = {}
	for func in bv.functions:
		caller = hex(int(func.start))
		cg[caller] = []
		for inst in func.instructions:
			if func.is_call_instruction(inst[1]):
				if str(inst[0][-1]).startswith("0x"):
					if str(inst[0][-1]) not in cg[caller]:
						cg[caller].append(str(inst[0][-1]))
			if str(inst[0][0] == 'b'):
				des = str(inst[0][-1])
				if des in funcs.keys() and des not in cg[caller]:
					cg[caller].append(des)

	f = open("%scg.txt" % (path) , "w")
	for caller in cg.keys():
		if cg[caller] != []:
			for callee in cg[caller]:
				f.write("%s -> %s\n" % (caller , callee))
	f.close()
	print("get cg")

	# Create CFG
	cfg = {}
	for func in bv.functions:
		func_name = hex(int(func.start))
		cfg[func_name] = {}
		for bb in func.basic_blocks:
			caller = hex(int(bb.start))
			cfg[func_name][caller] = []
			for edge in bb.outgoing_edges:
				callee = hex(int(edge.target.start))
				if callee not in cfg[func_name][caller]:
					cfg[func_name][caller].append(callee)

	f = open("%scfg.txt" % (path) , "w")
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
	print("get cfg")

	# Find path in func level
	cg_path = []
	start = '0x100a0'
	end = '0xd69c'
	findpath_cg(start, end, cg, cg_path)

	f = open("%scg_path.txt" % (path) , "w")
	for i in cg_path:
		for j in i[:-1]:
			f.write("%s -> " % (j))
		f.write("%s\n" % (i[-1]))
	f.close()
	print("get cg_path")

	# Find path intro func in bb level
	cfg_path = {}

	path = path +'cfg_path/'
	isExists=os.path.exists(path)
	if not isExists:
		os.makedirs(path) 
		print(path+' Create dir success')
	else:
		print(path+' already exists')

	for i in cg_path:
		for j in range(len(i)-1):
			start = i[j]
			end = i[j+1]
			name = "%s->%s" % (start, end)
			if name not in cfg_path.keys():
				print(name)
				cfg_path[name] = {}
				findpath_cfg(start, end, cfg[start], cfg_path[name])
				f = open("%s%s.txt" % (path, name) , "w")
				for i in cfg_path[name].keys():
					f.write("%s\n" % (i))
					for j in cfg_path[name][i]:
						for k in j[:-1]:
							f.write("%s -> " % (k))
						f.write("%s\n" % (j[-1]))
	print("get cfg_path")