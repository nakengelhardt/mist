from migen.fhdl.structure import _Fragment

from fd import synthesize_fds
from lut import synthesize_luts

def synthesize(f):
	if not isinstance(f, _Fragment):
		f = f.get_fragment()
	synthesize_fds(f)
	synthesize_luts(f)
