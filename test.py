from migen.fhdl.std import *
from migen.fhdl import edif
from migen.fhdl.specials import Tristate

import mist

class Test(Module):
	def __init__(self):
		self.o = Signal()
		self.i = [Signal() for x in range(3)]
		self.a = Signal()
		self.b = Signal()
		self.x = Signal()
		self.t = Signal()

		self.sync += self.x.eq(self.a | self.b)
		self.comb += self.o.eq(self.i[0] & (self.i[1] | self.i[2]))
		self.specials += Tristate(self.t, self.o, self.i[0])
		self.clock_domains.cd_sys = ClockDomain()


t = Test()

f = t.get_fragment()


name = "Example"
device = "xc6slx45-fgg484-2"
cell_library = "UNISIMS"
vendor = "Xilinx"
ios = {t.o, t.a, t.b, t.x, t.cd_sys.clk, t.cd_sys.rst}
ios.update(t.i)

ios = set(mist.synthesize(f, ios).values())

print(edif.convert(f, ios, cell_library, vendor, device, name))
