from migen.fhdl.std import *
from migen.fhdl import edif
from migen.fhdl.tools import list_special_ios
import mist

class Test(Module):
	def __init__(self, i, o):
		self.comb += o.eq(i[0] & (i[1] | i[2]))


o = Signal()
i = [Signal() for x in range(3)]


t = Test(i, o).get_fragment()

mist.transform(t)

print(list_special_ios(t, True, True, True))

name = "Example"
device = "xc6slx45-fgg484-2"
cell_library = "UNISIMS"
vendor = "Xilinx"
ios = {o}
for x in i:
	ios.add(x)
print(edif.convert(t, ios, cell_library, vendor, device, name))

