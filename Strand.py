import angr
import pyvex

proj = angr.Project("./test1")
cfg = proj.analyses.CFG()

for i in cfg.functions.values():
	if i.name == 'main':
		func = i

class state(object):
	"""docstring for state"""
	id = 0
	tag = ''
	irsb = ''

	def __init__(self, id, tag, irsb, stmt):
		self.tag = tag
		self.id = id
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

def getid(state):
	return state.id

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
	st = None
	st = state(index,stmt.tag,irsb,stmt)
	index +=1
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

print(block.states)


# while len(uncover) > 0:
inst = uncover.pop()
srand = []
if inst.usevar != []:
	srand.append(inst)
	var_use = inst.usevar.copy()

while len(var_use)>0:
	for usev in var_use:
		for st in uncover:
			if usev in st.defvar:
				for v in st.usevar:
					var_use.append(v)
			if usev in st.usevar:
				for v in st.usevar:
					if v not in var_use:
						var_use.append(v)
		for st in uncover:
			if usev in st.defvar:
				srand.append(st)
				uncover.remove(st)
				var_use.remove(usev)
			if usev in st.usevar:
				srand.append(st)
				uncover.remove(st)
		if usev in var_use:
			var_use.remove(usev)

srand.sort(key=getid)
for r in srand:
	r.stmt.pp()

bb.vex.pp()