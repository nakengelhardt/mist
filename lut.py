from collections import OrderedDict

from migen.fhdl.std import *
from migen.fhdl.structure import _Fragment, _Operator, _Assign
from migen.fhdl.specials import Tristate
from migen.fhdl.tools import list_special_ios

def _eval_op(node, sigval):
	if isinstance(node, _Operator):
		if node.op == "|":
			return _eval_op(node.operands[0], sigval) | _eval_op(node.operands[1], sigval)
		if node.op == "&":
			return _eval_op(node.operands[0], sigval) & _eval_op(node.operands[1], sigval)
		if node.op == "^":
			return _eval_op(node.operands[0], sigval) ^ _eval_op(node.operands[1], sigval)
		if node.op == "~":
			return ~_eval_op(node.operands[0], sigval)
	if isinstance(node, Signal):
		assert sigval[node] != None
		return sigval[node]

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
		tr = _build_tt(node, sigval, ui[0:-1])
		sigval[s] = 1
		tl = _build_tt(node, sigval, ui[0:-1])
		sigval[s] = None
		return (tl << len(ui)) | tr 

def _build_lut(node, sigval, i, o):
	size = len(i)
	tt = _build_tt(node, sigval, i)
	inputs = {}
	for k in range(size):
		inputs["i_I{}".format(k)]=i[k]
	return Instance("LUT{}".format(size), o_O=o, p_INIT=("{:0"+str(2**(max(0,size-2)))+"X}").format(tt), **inputs)
	
def _build_mux6(I0, I1, I2, I3, s0, s1, o):
	return Instance("LUT6", i_I0=s0, i_I1=I1, i_I2=s1, i_I3=I1, i_I4=I0, i_I5=I2, o_O=o, p_INIT="DFD5DAD08F858A80")

def _build_luts(node, sigval, o):
	if list(sigval.values()).count(None) > 6:
		luts = []
		s = filter(lambda k,v : v == None, sigval.items())
		s0,s1 = s[0],s[1]
		I0,I1,I2,I3 = [Signal() for i in range(4)]
		sigval[s0], sigval[s1] = 0, 0
		luts += _build_luts(node, sigval, I0)
		sigval[s0], sigval[s1] = 0, 1
		luts += _build_luts(node, sigval, I1)
		sigval[s0], sigval[s1] = 1, 0
		luts += _build_luts(node, sigval, I2)
		sigval[s0], sigval[s1] = 1, 1
		luts += _build_luts(node, sigval, I3)
		luts += [_build_mux6(I0,I1,I2,I3,s0,s1,o)]
		sigval[s0], sigval[s1] = None, None
		return luts
	else:
		return [_build_lut(node, sigval, [k for k,v in sigval.items() if v == None], o)]

def _build_iobufs(ins, outs):
	bufs = []
	newios = {}
	for i in ins:
		ibuf = Signal(related=i)
		newios[i]=ibuf
		bufs.append(Instance("IBUF", i_I=ibuf, o_O=i))		
	for o in outs:
		obuf = Signal(related=o)
		newios[o]=obuf
		bufs.append(Instance("OBUF", i_I=o, o_O=obuf))			
	return newios, bufs
	

def synthesize_luts(f, ios):
	for tri in f.specials:
		if isinstance(tri, Tristate):
			notoe = Signal(related=tri.oe)
			f.comb.append(notoe.eq(~tri.oe))
			f.specials.add(Instance("IOBUF", i_I=tri.o, i_T=notoe, o_O=tri.i, io_IO=tri.target))
			f.specials.remove(tri)
	#entrances to instances can contain expressions... move these to comb here later
	for a in f.comb:
		if not isinstance(a, _Assign):
			raise NotImplementedError("Assign statements only (got {0})".format(a))
		sigval = OrderedDict()
		_build_sigval(a.r, sigval)
		f.specials.update(_build_luts(a.r, sigval, a.l))
	f.comb = []
	outs = list_special_ios(f, False, True, False)
	ins = ios - list_special_ios(f, False, True, True)
	newios, iobufs = _build_iobufs(ins, outs)
	f.specials.update(iobufs)
	return newios
