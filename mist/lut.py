from collections import OrderedDict

from migen.fhdl.std import *
from migen.fhdl.structure import _Operator, _Assign

def _eval_op(node, sigval):
	if isinstance(node, _Operator):
		if node.op == "|":
			return _eval_op(node.operands[0], sigval) | _eval_op(node.operands[1], sigval)
		if node.op == "&":
			return _eval_op(node.operands[0], sigval) & _eval_op(node.operands[1], sigval)
		if node.op == "^":
			return _eval_op(node.operands[0], sigval) ^ _eval_op(node.operands[1], sigval)
		if node.op == "~":
			return ~_eval_op(node.operands[0], sigval) & 1
		if node.op == "m":
			return _eval_op(node.operands[1], sigval) if _eval_op(node.operands[0], sigval) else _eval_op(node.operands[2], sigval)
		if node.op == "==":
			return _eval_op(node.operands[0], sigval) == _eval_op(node.operands[1], sigval)
		if node.op == "!=":
			return _eval_op(node.operands[0], sigval) != _eval_op(node.operands[1], sigval)
	if isinstance(node, Signal):
		assert sigval[node] != None
		return sigval[node]
	if isinstance(node, int):
		assert 0 <= node <= 1
		return node
	if isinstance(node, bool):
		if node:
			return 1
		else:
			return 0
	raise ValueError("Unsupported node type ({})".format(node))

def _build_sigval(node, sigval):
	if isinstance(node, _Operator):
		for o in node.operands:
			_build_sigval(o, sigval)
	if isinstance(node, Signal):
		sigval[node] = None

def _build_tt(node, sigval, ui):
	if ui == []:
		return _eval_op(node, sigval)
	else:
		s = ui[-1]
		sigval[s] = 0
		tr = _build_tt(node, sigval, ui[:-1])
		sigval[s] = 1
		tl = _build_tt(node, sigval, ui[:-1])
		sigval[s] = None
		return (tl << 2**(len(ui) - 1)) | tr 

def _build_lut(node, sigval, i, o):
	size = len(i)
	if size > 0:
		tt = _build_tt(node, sigval, i)
		inputs = {}
		for k in range(size):
			inputs["i_I{}".format(k)]=i[k]
		return Instance("LUT{}".format(size), o_O=o, p_INIT=("{:0"+str(2**(max(0,size-2)))+"X}").format(tt), **inputs)
	else:
		if _eval_op(node, sigval):
			return Instance("VCC", o_P=o)
		else:
			return Instance("GND", o_G=o)
	
def _build_mux6(I0, I1, I2, I3, s0, s1, o):
	return Instance("LUT6", i_I0=s0, i_I1=I1, i_I2=s1, i_I3=I1, i_I4=I0, i_I5=I2, o_O=o, p_INIT="DFD5DAD08F858A80")

def _build_luts(node, sigval, o):
	if list(sigval.values()).count(None) > 6:
		luts = []
		s = filter(lambda k,v : v == None, sigval.items())
		s0, s1 = s[0], s[1]
		I0, I1, I2, I3 = [Signal() for i in range(4)]
		sigval[s0], sigval[s1] = 0, 0
		luts += _build_luts(node, sigval, I0)
		sigval[s0], sigval[s1] = 0, 1
		luts += _build_luts(node, sigval, I1)
		sigval[s0], sigval[s1] = 1, 0
		luts += _build_luts(node, sigval, I2)
		sigval[s0], sigval[s1] = 1, 1
		luts += _build_luts(node, sigval, I3)
		luts += [_build_mux6(I0, I1, I2, I3, s0, s1, o)]
		sigval[s0], sigval[s1] = None, None
		return luts
	else:
		return [_build_lut(node, sigval, [k for k, v in sigval.items() if v == None], o)]


def synthesize_luts(f):
	for a in f.comb:
		if not isinstance(a, _Assign):
			raise NotImplementedError("Assign statements only (got {0})".format(a))
		sigval = OrderedDict()
		_build_sigval(a.r, sigval)
		f.specials.update(_build_luts(a.r, sigval, a.l))
	f.comb = []
