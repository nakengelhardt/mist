from migen.fhdl.std import *
from migen.fhdl import edif
from migen.fhdl.specials import Tristate
from mibuild.platforms import m1

import mist

class Test(Module):
	def __init__(self, a, b, x, o):
		self.sync += x.eq(a | b)
		self.comb += o.eq(a & b)

m1 = m1.Platform()

a = m1.request("user_btn")
b = m1.request("user_btn")
x = m1.request("user_led")
o = m1.request("user_led")

t = Test(a, b, x, o)

m1.build(t, mode="mist")