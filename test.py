from migen.fhdl.std import *
from mibuild.platforms import m1

from mist.arithmetic import CarryLookaheadAdder

class Test(Module):
	def __init__(self, led1, led2):
		c = Signal(8)
		d = Signal(8)
		d_next = Signal(8)
		self.sync += d.eq(d_next), c.eq(c+1)
		self.submodules += CarryLookaheadAdder(d, 1, d_next)
		self.comb += led1.eq(d[7]), led2.eq(c[7])

def main():
	plat = m1.Platform()

	led1 = plat.request("user_led")
	led2 = plat.request("user_led")
	
	t = Test(led1, led2)

	# f = t.get_fragment()
	# plat.finalize(f)
	# mist.synthesize(f, plat.constraint_manager.get_io_signals())
	# v_src, named_sc, named_pc = plat.get_verilog(f)
	# print(v_src)

	plat.build(t, mode="verilog", run=False)
	#plat.build(t)

if __name__ == '__main__':
	main()
