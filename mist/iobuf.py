from migen.fhdl.std import *
from migen.fhdl.specials import Tristate
from migen.fhdl.tools import list_special_ios, list_targets
from migen.fhdl.visit import NodeTransformer


def _build_iobufs(ins, outs):
	bufs = []
	bufferedios = {}
	for i in ins:
		ibuf = Signal(related=i)
		bufferedios[i]=ibuf
		bufs.append(Instance("IBUF", i_I=i, o_O=ibuf))
	for o in outs:
		obuf = Signal(related=o)
		bufferedios[o]=obuf
		bufs.append(Instance("OBUF", i_I=obuf, o_O=o))
	return bufferedios, bufs

class IOReplacer(NodeTransformer):
	def __init__(self, bufferedios):
		self.bufferedios = bufferedios

	def visit_Signal(self, node):
		try:
			return self.bufferedios[node]
		except KeyError:
			return node	

def _replace_iosigs(f, bufferedios):
	replacer = IOReplacer(bufferedios)
	f.comb = replacer.visit(f.comb)
	f.sync = replacer.visit(f.sync)
	for sp in f.specials:
		for obj, attr, x in sp.iter_expressions():
			expr = getattr(obj, attr)
			setattr(obj, attr, replacer.visit(expr))
	for dom in f.clock_domains:
		if dom.clk in bufferedios:
			dom.clk = bufferedios[dom.clk]
		if dom.rst is not None and dom.rst in bufferedios:
			dom.rst = bufferedios[dom.rst]

def add_iobufs(f, ios):
	for tri in f.specials:
		if isinstance(tri, Tristate):
			f.specials.add(Instance("IOBUF", i_I=tri.o, i_T=~tri.oe, o_O=tri.i, io_IO=tri.target))
			f.specials.remove(tri)
	outs = ios & (list_targets(f) | list_special_ios(f, False, True, False))
	inouts = ios & (list_special_ios(f, False, False, True))
	ins = ios - outs - inouts
	bufferedios, iobufs = _build_iobufs(ins, outs)
	_replace_iosigs(f, bufferedios)
	f.specials.update(iobufs)
