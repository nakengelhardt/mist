from migen.fhdl.structure import _Fragment

from fd import synthesize_fds
from lut import synthesize_luts
from iobuf import add_iobufs
from lowering import extract_special_expr

def synthesize(f, ios):
	if not isinstance(f, _Fragment):
		f = f.get_fragment()
	newios = add_iobufs(f,ios)
	extract_special_expr(f)
	synthesize_fds(f)
	synthesize_luts(f)
