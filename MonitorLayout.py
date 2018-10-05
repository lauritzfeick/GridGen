import numpy as np


# stores the layout (which psd-files should be used) for one monitor
class MonitorLayout(object):

    def __init__(self, monitor_id):
        self.monitor_id = monitor_id
        self.h = 0
        self.w = 0
        self.grid_ids = np.ones((10,10), dtype=np.int) * -1

    def set_grid_id(self, x, y, id):
        new_h = max(y+1,self.h)
        new_w = max(x+1,self.w)
        (h,w) = np.shape(self.grid_ids) # allocated space
        if (x < w) and (y < h):
            self.grid_ids[y,x] = id
        else:
            # make new grid twice as big as necessary
            np.concatenate(self.grid_ids, -1*np.ones((self.h, new_w*2-w), dtype=np.int),axis=1)
            np.concatenate(self.grid_ids, -1*np.ones((new_h*2-h, new_w*2), dtype=np.int), axis=0)
            self.grid_ids[y,x] = id
        self.h = new_h
        self.w = new_w

    def get_grid_id(self, x, y):
        if (x < self.w) and (y < self.h):
            return self.grid_ids[y,x]
        else:
            return -1

    def print(self):
        print_string = '{0} {2} {1}('.format(self.monitor_id, self.h, self.w)
        for y in range(self.h):
            for x in range(self.w):
                print_string += '{0} {1} {2},'.format(x,y,self.grid_ids[y,x])

        print_string = print_string[:-1]
        print_string += (')')
        print(print_string)

    @staticmethod
    def parse_layout(input: str):
        """
        Parses a given input string (usually from the ui). The format should be the following for one monitor:
        <mon_id>(<grid_id>)

        or (if multiple grids should be used for the monitor - for Nvidia Sourround / AMD Eyefinity):
        <mon_id> <num_grids_horizontal> <num_grids_vertical>(<grid_id>)

        or (if multiple different grids should be used):
        <mon_id> <num_grids_horizontal> <num_grids_vertical>(<pos_x> <pos_y> <grid_id>;<pos_x> ...)
        In this case, every subgrid must be specified.

        This must be done for each monitor, in a new line.

        Example
        -------
        To place grid 5 on monitor 1
        and grid 7 on monitor 2, type:
        1(5)
        2(7)

        To place three different grids 4,5,6 horizontal on a 5760x1080 (3*FHD) monitor, type:
        1(1 1 4;2 1 5;3 1 6)
        """
        lines = input.split('\n')
        if len(lines) < 1:
            raise ValueError("Specify at least one monitor!")

        monitor_layouts = []

        for l in lines:
            if len(l) < 4:
                break

            l = l.replace(')', '')
            l = l.split('(', maxsplit=1)
            monitor_id = int(l[0])
            layout = l[1].split(',')

            if len(layout) == 1: # Only one layout used for this monitor.
                mon_layout = MonitorLayout(monitor_id)
                mon_layout.h = 1
                mon_layout.w = 1
                mon_layout.set_grid_id(0, 0, int(layout[0]))
                monitor_layouts.append(mon_layout)

            else:
                mon_layout = MonitorLayout(monitor_id)
                for sl in layout: # Multiple layouts used for this monitor.
                    sl = sl.strip(' ')
                    sub_layout = sl.split(' ')
                    pos_x = int(sub_layout[0])
                    pos_y = int(sub_layout[1])
                    grid_id = int(sub_layout[2])
                    mon_layout.set_grid_id(pos_x, pos_y, grid_id)
                monitor_layouts.append(mon_layout)

        return monitor_layouts