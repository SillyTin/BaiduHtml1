import angr
import pyvex

proj = angr.Project("./test1")
cfg = proj.analyses.CFG()

for i in cfg.functions.values():
	if i.name == 'main':
		func = i

class state(object):
	"""docstring for state"""
	tag = ''
	irsb = ''

	def __init__(self, tag, irsb, stmt):
		self.tag = tag
		self.irsb = irsb
		self.stmt = stmt
		self.defvar = []
		self.usevar = []

	def adddefvar(self, var):
		self.defvar.append(var)

	def addusevar(self, var):
		self.usevar.append(var)


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

bb = list(func.blocks)[0] 
irsb = bb.vex
block = IRblock(irsb.addr) 
IRblocks.append(block)


index = 0
for stmt in irsb.statements:
	print("in the %d loop" %index)
	index +=1
	st = None
	st = state(stmt.tag,irsb,stmt)
	if isinstance(st.stmt, pyvex.IRStmt.IMark):
		continue
	elif isinstance(st.stmt, pyvex.IRStmt.WrTmp):
		st.adddefvar('t'+str(st.stmt.tmp))
		for ex in st.stmt.expressions:
			if isinstance(ex, pyvex.IRExpr.RdTmp):
				st.addusevar(str(ex))
			elif isinstance(ex, pyvex.IRExpr.Get):
				st.addusevar("Offset"+str(ex.offset))
	elif isinstance(st.stmt, pyvex.IRStmt.Put):
		if isinstance(st.stmt.data, pyvex.IRExpr.RdTmp):
			st.addusevar(str(st.stmt.data))
		st.adddefvar("Offset"+str(st.stmt.offset))
	elif isinstance(st.stmt, pyvex.IRStmt.AbiHint):
		continue
	else:
		print("Unknown:"+stmt.tag)

	block.states.append(st)
	uncover.append(st)

	print(st.defvar)
	print(st.usevar)
	# del st 

print(block.states)


# while len(uncover) > 0:
# 	inst = uncover.pop()
# 	srand = []
# 	var_def = inst.defvar.copy()
# 	var_use = inst.usevar.copy()

# for stmt in irsb.statements:
# 	if isinstance(stmt, pyvex.IRStmt.Get):
# 		var_def.append(stmt.tmp)
# 		var_use.append(stmt.data)

bb.vex.pp()