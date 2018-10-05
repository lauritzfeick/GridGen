from MonitorLayout import MonitorLayout

ml = MonitorLayout(0)
ml.set_grid_id(0,1, 42)
ml.print()
print(ml.grid_ids)

print()
layout_str = '0(1)\n1(0 0 4, 1 1 2)'
print(layout_str)
print('-----------------------')
mls = MonitorLayout.parse_layout(layout_str)
for ml in mls:
    ml.print()

