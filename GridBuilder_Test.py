from GridBuilder import compute_gridstr
from MonitorLayout import MonitorLayout
import os


inpath = os.path.abspath("example_psd\\test2.psd")

# test one layout per monitor
outpath = os.path.abspath("example_psd\\test.grid")
ml = MonitorLayout.parse_layout("0(0)")
str = compute_gridstr(ml, [inpath])
f = open(outpath, 'w+')
f.write(str)
f.close()

# test 3 layouts per monitor
outpath = os.path.abspath("example_psd\\test_multilayout.grid")
ml = MonitorLayout.parse_layout("0(0 0 0, 1 0 0, 2 0 0)")
str = compute_gridstr(ml, [inpath])
f = open(outpath, 'w+')
f.write(str)
f.close()

# test 2 monitors
outpath = os.path.abspath("example_psd\\test_multimon.grid")
ml = MonitorLayout.parse_layout("0(0)\n1(0)")
str = compute_gridstr(ml, [inpath])
f = open(outpath, 'w+')
f.write(str)
f.close()

print("fin")