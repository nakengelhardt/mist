from migen.fhdl.std import *
from mibuild.platforms import m1

import mist

class Test(Module):
	def __init__(self, a, b, x, o):
		self.sync += x.eq(a | b)
		self.comb += o.eq(a & b), If(a, b.eq(x)).Else(b.eq(a))

m1 = m1.Platform()

a = m1.request("user_btn")
b = m1.request("user_btn")
x = m1.request("user_led")
o = m1.request("user_led")

t = Test(a, b, x, o)

#f = t.get_fragment()
#m1.finalize(f)
#mist.synthesize(f, m1.constraint_manager.get_io_signals())
#v_src, named_sc, named_pc = m1.get_verilog(f)
#print(v_src)

m1.build(t, mode="mist", run=False)
