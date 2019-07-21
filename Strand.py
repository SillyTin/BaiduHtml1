import angr

proj = angr.Project("./test1")
cfg = proj.analyses.CFG()

for i in cfg.functions.values():
	if i.name == 'main':
		func = i

class state(object):
	"""docstring for state"""
	tag = ''
	irsb = ''
	defvar = []
	usevar = []

	def __init__(self, tag, defvar, usevar, irsb, stmt):
		self.tag = tag
		self.irsb = irsb
		self.stmt = stmt
		self.defvar = defvar.copy()
		self.usevar = usevar.copy()

class IRblock(object):
	"""docstring for IRblock"""
	addr = ''
	states = []

	def __init__(self, addr):
		self.addr = addr
	
	def addstate(self, state):
		self.states.append(state)

var_def = []
var_use = []
strand = []
uncover = []
IRblocks = []

for i in func.blocks:
	bb = i
	irsb = bb.vex
	block = IRblock(irsb.addr)
	IRblocks.append(blcok)

	for stmt in irsb.statements:

		uncover.append(stmt)

	while len(uncover) > 0:
		inst = uncover.pop()
		if isinstance(isnt, pyvex.IRStmt.Get):
			var_def.append(stmt.tmp)
			var_use.append(stmt.data)

	for stmt in irsb.statements:
		if isinstance(stmt, pyvex.IRStmt.Get):
			var_def.append(stmt.tmp)
			var_use.append(stmt.data)

bb.vex.pp()