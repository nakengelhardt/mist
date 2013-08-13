from migen.fhdl.std import *
from mibuild.platforms import m1

import mist

class Test(Module):
	def __init__(self, btn1, btn2, btn3, led1, led2):
		self.sync += led1.eq(btn1 | btn2)
		self.comb += [
			led2.eq(1),
			If(btn3, led2.eq(btn1 | btn2)).Else(led2.eq(btn1 & btn2))
		]

m1 = m1.Platform()

btn1, btn2, btn3 = (m1.request("user_btn") for i in range(3))
led1, led2 = (m1.request("user_led") for i in range(2))

t = Test(btn1, btn2, btn3, led1, led2)

#f = t.get_fragment()
#m1.finalize(f)
#mist.synthesize(f, m1.constraint_manager.get_io_signals())
#v_src, named_sc, named_pc = m1.get_verilog(f)
#print(v_src)

m1.build(t, mode="mist")
