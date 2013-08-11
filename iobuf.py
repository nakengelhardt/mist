from migen.fhdl.std import *
from migen.fhdl.specials import Tristate
from migen.fhdl.tools import list_special_ios, list_targets

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

def add_iobufs(f, ios):
	for tri in f.specials:
		if isinstance(tri, Tristate):
			notoe = Signal(related=tri.oe)
			f.comb.append(notoe.eq(~tri.oe))
			f.specials.add(Instance("IOBUF", i_I=tri.o, i_T=notoe, o_O=tri.i, io_IO=tri.target))
			f.specials.remove(tri)
	outs = ios & (list_targets(f) | list_special_ios(f, False, True, False))
	inouts = ios & (list_special_ios(f, False, False, True))
	ins = ios - outs - inouts
	newios, iobufs = _build_iobufs(ins, outs)
	f.specials.update(iobufs)
	return newios
