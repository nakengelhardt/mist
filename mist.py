from migen.fhdl.structure import _Fragment

from fd import synthesize_fds
from lut import synthesize_luts

def synthesize(f, ios):
	if not isinstance(f, _Fragment):
		f = f.get_fragment()
	synthesize_fds(f)
	newios = synthesize_luts(f, ios)
	return newios
