from migen.fhdl.size import value_bits_sign
from migen.fhdl.std import *
from migen.fhdl.tools import list_signals

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
