from migen.fhdl.structure import _Fragment

from mist.fd import synthesize_fds
from mist.lut import synthesize_luts
from mist.iobuf import add_iobufs
from mist.lowering import extract_special_expr, lower_processes

def synthesize(f, ios):
	if not isinstance(f, _Fragment):
		f = f.get_fragment()
	add_iobufs(f, ios)
	extract_special_expr(f)
	synthesize_fds(f)
	lower_processes(f, ios)
	synthesize_luts(f)
