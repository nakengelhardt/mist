from migen.fhdl.std import *
from migen.fhdl.structure import _Fragment, _Operator, _Assign
from collections import OrderedDict

def eval_op(node, sigval):
	if isinstance(node, _Operator):
		if node.op == "|":
			return eval_op(node.operands[0], sigval) or eval_op(node.operands[1], sigval)
		if node.op == "&":
			return eval_op(node.operands[0], sigval) and eval_op(node.operands[1], sigval)
		if node.op == "^":
			return eval_op(node.operands[0], sigval) is not eval_op(node.operands[1], sigval)
		if node.op == "~":
			return not eval_op(node.operands[0], sigval)
	if isinstance(node, Signal):
		assert sigval[node] != None
		return sigval[node]

def list_signals(node, sigval):
	if isinstance(node, _Operator):
		for o in node.operands:
			list_signals(o, sigval)
	if isinstance(node, Signal):
		sigval[node] = None

def build_tt(node, sigval, ui):
	if ui == []:
		return int(eval_op(node, sigval))
	else:
		s = ui[-1]
		sigval[s] = False
		tr = build_tt(node, sigval, ui[0:-1])
		sigval[s] = True
		tl = build_tt(node, sigval, ui[0:-1])
		sigval[s] = None
		return (tl << len(ui)) | tr 

def build_lut(node, sigval, i, o):
	size = len(i)
	tt = build_tt(node, sigval, i)
	inputs = {}
	for k in range(size):
		inputs["i_I{}".format(k)]=i[k]
	return Instance("LUT{}".format(size), o_O=o, p_INIT=("{:0"+str(2**(size-2))+"X}").format(tt), **inputs)
	
def build_mux6(I0,I1,I2,I3,s0,s1,o):
	return Instance("LUT6", i_I0=s0, i_I1=I1, i_I2=s1, i_I3=I1, i_I4=I0, i_I5=I2, o_O=o, p_INIT="DFD5DAD08F858A80")

def build_luts(node, sigval, o):
	if list(sigval.values()).count(None) > 6:
		luts = []
		s = filter(lambda k,v : v == None, sigval.items())
		s0,s1 = s[0],s[1]
		I0,I1,I2,I3 = [Signal() for i in range(4)]
		sigval[s0], sigval[s1] = False, False
		luts += build_luts(node, sigval, I0)
		sigval[s0], sigval[s1] = False, True
		luts += build_luts(node, sigval, I1)
		sigval[s0], sigval[s1] = True, False
		luts += build_luts(node, sigval, I2)
		sigval[s0], sigval[s1] = True, True
		luts += build_luts(node, sigval, I3)
		luts += [build_mux6(I0,I1,I2,I3,s0,s1,o)]
		sigval[s0], sigval[s1] = None, None
		return luts
	else:
		return [build_lut(node, sigval, [k for k,v in sigval.items() if v == None], o)]

def transform(f):
	if not isinstance(f, _Fragment):
		f = f.get_fragment()
	if f.sync != {} :
		raise NotImplementedError("No synchronous statements yet")
	for a in f.comb:
		if not isinstance(a, _Assign):
			raise NotImplementedError("Assign statements only")
		sigval = OrderedDict()
		list_signals(a.r, sigval)
		f.specials.add(*build_luts(a.r, sigval, a.l))
	f.comb = []
	
