from collections import OrderedDict

from migen.fhdl.size import value_bits_sign
from migen.fhdl.std import *
from migen.fhdl.tools import list_signals
from migen.fhdl.structure import _Assign

def extract_special_expr(f):
	for sp in f.specials:
		for obj, attr, x in sp.iter_expressions():
			expr = getattr(obj, attr)
			if not isinstance(expr, Signal):
				rell = list_signals(expr)
				if rell:
					rel = min(rell, key=lambda x: x.huid)
				else:
					rel = None
				s_expr = Signal(value_bits_sign(expr), related=rel)
				f.comb.append(s_expr.eq(expr))
				setattr(obj, attr, s_expr)


def _build_conditional_expr(condcontext, node, sd=None):
	if sd is None:
		sd = OrderedDict()

	if isinstance(node, (list, tuple)):
		for statement in node:
			_build_conditional_expr(condcontext, statement, sd)

	if isinstance(node, _Assign):
		assert(isinstance(node.l, Signal))	
		l = node.l
		t = node.r
		if condcontext is not None:
			if l in sd:
				f = sd[l]
			else:
				f = l.reset
			sd[l] = Mux(condcontext, t, f)
		else:
			sd[l] = t

	if isinstance(node, If):
		if condcontext is not None:
			cond = condcontext & node.cond
			notcond = condcontext & (~node.cond)
		else:
			cond = node.cond
			notcond = ~node.cond
		_build_conditional_expr(cond, node.t, sd)
		_build_conditional_expr(notcond, node.f, sd)

	if isinstance(node, Case):
		defaultcond = None
		for k in node.cases.keys():
			if k != "default":
				if condcontext is not None:
					cond = condcontext & (node.test == k)
				else:
					cond = (node.test == k)
				if defaultcond is not None:
					defaultcond = defaultcond & (node.test != k)
				else:
					defaultcond = (node.test != k)
				_build_conditional_expr(cond, node.cases[k], sd)
		#default
		if "default" in node.cases:
			if defaultcond is not None:
				if condcontext is not None:
					cond = condcontext & defaultcond
				else:
					cond = defaultcond
			else:
				cond = condcontext
			_build_conditional_expr(cond, node.cases["default"], sd)
	
	return sd

def lower_conditionals(f):
	# gets called after synthesize_fd, so sync is already empty
	sd = _build_conditional_expr(None, f.comb)
	f.comb = [k.eq(sd[k]) for k in sd.keys()]
