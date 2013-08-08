from collections import OrderedDict

from migen.fhdl.std import *
from migen.fhdl.tools import insert_resets
from migen.fhdl.specials import Instance
from migen.fhdl.structure import _Assign
from migen.fhdl.visit import NodeTransformer

class _NextTargetInserter(NodeTransformer):
	def __init__(self):
		self.registers = OrderedDict()

	def visit_Assign(self, node):
		# visit left handside only
		return _Assign(self.visit(node.l), node.r)

	def visit_Signal(self, node):
		try:
			return self.registers[node]
		except KeyError:
			next = Signal((node.nbits, node.signed), related=node)
			self.registers[node] = next
			return next

def synthesize_fds(f):
	# disable reset insertion for now (comb synthesizer does not support If)
	#insert_resets(f)
	for clk, statements in f.sync.items():
		inserter = _NextTargetInserter()
		statements = inserter.visit(statements)
		for q, d in inserter.registers.items():
			f.specials.add(Instance("FD", i_D=d, o_Q=q, i_C=f.clock_domains[clk].clk))
		f.comb += statements
	f.sync = dict()
