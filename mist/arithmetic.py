from migen.fhdl.std import *
from migen.fhdl.size import value_bits_sign

def _give_bits(e, extend=False):
	if isinstance(e, Value):
		l,s = value_bits_sign(e)
		for n in range(l):
			yield e[n]
		if extend:
			while True:
				if s:
					yield e[l-1]
				else:
					yield 0
	elif isinstance(e, bool):
		if e:
			yield 1
		else:
			yield 0
		if extend:
			while True:
				yield 0
		else:
			return
	elif isinstance(e, int):
		n = e
		s = 1 if e < 0 else 0
		while n != 0:
			yield n & 1
			n = n >> 1
		if extend:
			while True:
				yield s
		else:
			return
	else:
		raise ValueError("I don't know how to slice {}.".format(e))

class Halfadder(Module):
	def __init__(self, a, b, s, c):
		self.comb += s.eq(a ^ b), c.eq(a & b)

class Fulladder(Module):
	def __init__(self, a, b, s, cin, cout):
		s1 = Signal()
		c1 = Signal()
		c2 = Signal()
		self.submodules.h1 = Halfadder(a, b, s1, c1)
		self.submodules.h2 = Halfadder(s1, cin, s, c2)
		self.comb += cout.eq(c1 | c2)

class RippleCarry(Module):
	def __init__(self, a, b, s, sub=False):
		bits, signed = value_bits_sign(s)
		cin = 0
		carry = Signal()
		op1 = _give_bits(a, extend=True)
		op2 = _give_bits(~b, extend=True) if sub else _give_bits(b, extend=True)
		for bop1, bop2, res in zip(op1, op2, _give_bits(s, extend=False)):
			self.submodules += Fulladder(bop1, bop2, res, cin, carry)
			cin = carry
			carry = Signal()

class RippleCarryAdder(RippleCarry):
	def __init__(self, a, b, s):
		RippleCarry.__init__(self, a, b, s, sub=False)

class RippleCarrySubtractor(RippleCarry):
	def __init__(self, a, b, s):
		RippleCarry.__init__(self, a, b, s, sub=True)
