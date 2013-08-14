from migen.fhdl.std import *
from mibuild.platforms import m1

import mist

class Test(Module):
	def __init__(self, btn1, btn2, btn3, led1, led2):
		self.sync += led1.eq(0)
		self.comb += [
			led2.eq(1),
			If(btn3, led2.eq(btn1 | btn2)).Else(led2.eq(btn1 & Signal()))
		]

def main():
	plat = m1.Platform()

	btn1 = plat.request("user_btn")
	btn2 = plat.request("user_btn")
	btn3 = plat.request("user_btn")
	led1 = plat.request("user_led")
	led2 = plat.request("user_led")

	t = Test(btn1, btn2, btn3, led1, led2)

	# f = t.get_fragment()
	# plat.finalize(f)
	# mist.synthesize(f, plat.constraint_manager.get_io_signals())
	# v_src, named_sc, named_pc = plat.get_verilog(f)
	# print(v_src)

	plat.build(t, mode="mist", run=False)
	#plat.build(t)

if __name__ == '__main__':
	main()
