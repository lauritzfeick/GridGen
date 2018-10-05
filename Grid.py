from psd_tools import PSDImage
import threading
import math
import numpy as np


# Represents a grid, parsed from a psd-file.
class Grid(object):

    def __init__(self, psd_image_path):
        self.triggers = [] # A list of all triggers. A trigger is a list: top, bottom, left, right - all inclusive, relative pos
        self.gridboxes = [] # A list of all grids. A trigger is a list: top, bottom, left, right - all inclusive, relative pos
        self.h = 0 # image height
        self.w = 0 # image width
        self.num_layers = 0
        self.psd_image_path = psd_image_path
        self.psd_parse_thread = threading.Thread(target=self.parse_psd(),name='PSD_Parsing',daemon=True)
        self.psd_parse_thread.start()

    def print(self):
        self.psd_parse_thread.join()
        print('---------------------------------------')
        print('Grid:')
        print(self.psd_image_path)
        print('h: ', self.h)
        print('w: ', self.w)
        print('num layers: ', self.num_layers)
        print('triggers: ')
        print('top, bottom, left, right')
        for t in self.triggers:
            for i in t:
                print(i, '  ', end='')
            print()

        print('gridboxes: ')
        print('top, bottom, left, right')
        for gb in self.gridboxes:
            for i in gb:
                print(i, '  ', end='')
            print()

    def get_gridboxes(self):
        self.psd_parse_thread.join()
        return self.gridboxes

    def get_triggers(self):
        self.psd_parse_thread.join()
        return self.triggers

    def get_num_gridboxes(self):
        self.psd_parse_thread.join()
        return self.num_layers

    @staticmethod
    def find_rects(layers):
        # layers: list of psd-layers, that contain drawn rects.
        # return: lists of  top, bottom, left, right positions (inclusive) of the particular boxes/triggers
        n = len(layers)
        boxes = np.ones((4,n),dtype=np.int) * np.inf
        boxes[1, :] *= -1
        boxes[3, :] *= -1

        for i in range(n):
            layer = layers[i]
            pil_layer = layer.as_PIL()
            layer_offset_x, layer_offset_y, x1, y1 = layer.bbox
            layer_h = y1 - layer_offset_y
            layer_w = x1 - layer_offset_x
            for y in range(layer_h):
                for x in range(layer_w):
                    (r,g,b,a) = pil_layer.getpixel((x,y))
                    if a > 0:
                        if boxes[0,i] > y: # top
                            boxes[0,i] = y
                        elif boxes[1,i] < y: # bottom
                            boxes[1,i] = y
                        if boxes[2,i] > x: # left
                            boxes[2,i] = x
                        elif boxes[3,i] < x: # right
                            boxes[3,i] = x
            boxes[0, i] += layer_offset_y # top
            boxes[1, i] += layer_offset_y # bottom
            boxes[2, i] += layer_offset_x # left
            boxes[3, i] += layer_offset_x # right

        return boxes

    def parse_psd(self) -> None:
        # load the psd image
        psd = PSDImage.load(self.psd_image_path)
        self.num_layers = len(psd.layers) // 2
        _, _ , self.w, self.h = psd.bbox

        # iterate over layers, find the rect in each
        # even layers are boxes
        # uneven ones are triggers
        layers = psd.layers
        layers_triggers = []
        layers_boxes = []
        for layer_idx in range(0, math.floor(self.num_layers)):
            layers_boxes.append(layers[layer_idx*2 + 1])
            layers_triggers.append(layers[layer_idx*2])
        self.triggers = Grid.find_rects(layers_triggers)
        self.gridboxes = Grid.find_rects(layers_boxes)

    @staticmethod
    def __pos_string(name, mon_idx, rel_pos, a, b):
        #  mon_idx: in [0..n], gets incremented by 1 to fit GridMove specification.

        s = ''
        mon_idx += 1
        if rel_pos == 0:
            s = "  {0} = [Monitor{1}{3}]\n"
        elif rel_pos == 1:
            s = "  {0} = [Monitor{1}{3}] + [Monitor{1}{4}]\n"
        else:
            s = "  {0} = [Monitor{1}{3}] + [Monitor{1}{4}] * {2}\n"

        name = name.ljust(15,' ')
        return s.format(name, mon_idx, rel_pos, a, b)

    @staticmethod
    def _horz_pos_string(name, mon_idx, rel_pos):
        return Grid.__pos_string(name, mon_idx, rel_pos, 'Left  ', 'Width ')

    @staticmethod
    def _vert_pos_string(name, mon_idx, rel_pos):
        return Grid.__pos_string(name, mon_idx, rel_pos, 'Top   ', 'Height')

    def get_grid_string(self, monitor_idx:int, first_grid_idx:int, grids_in_monitor_x:int, grids_in_monitor_y:int,\
                        grid_pos_in_monitor_x:int, grid_pos_in_monitor_y:int) -> (int, str):
        # monitor_idx: Index of the monitor the grid shold be generated for. (index starts with 0)
        # grids_in_monitor_ : How many grids are used in each direction within this one monitor.
        # grid_pos_in_monitor_ : Where the gird is placed whithin the one monitor (index starts with 0)
        # first_grid_idx: The parsed grid contains (usually) multiple gridboxes, this is the index of the first gridbox.
        #   It gets incremented for the following.
        # return: tuple of the last used grid index and the computed string

        self.psd_parse_thread.join()
        grid_string = ""
        grid_counter = first_grid_idx - 1
        for idx in range(0,self.get_num_gridboxes()):
                grid_counter += 1
                trigger = self.triggers[:,idx]
                gridbox = self.gridboxes[:,idx]

                # relative offsets
                offset_left_rel_width = grid_pos_in_monitor_x / grids_in_monitor_x
                offset_top_rel_height = grid_pos_in_monitor_y / grids_in_monitor_y

                # create .grid sub-strings
                monitor = "[{0}]\n".format(grid_counter)
                # TRIGGERS
                trigger_top_pos_rel_height  = offset_top_rel_height + trigger[0] / (self.h) / grids_in_monitor_y
                trigger_bot_pos_rel_height  = offset_top_rel_height + (trigger[1] + 1)/ (self.h) / grids_in_monitor_y
                trigger_left_pos_rel_width  = offset_left_rel_width + trigger[2] / (self.w) / grids_in_monitor_x
                trigger_right_pos_rel_width = offset_left_rel_width + (trigger[3] + 1) / (self.w) / grids_in_monitor_x
                trigger_top   = Grid._vert_pos_string('TriggerTop',  monitor_idx, trigger_top_pos_rel_height)
                trigger_bot   = Grid._vert_pos_string('TriggerBottom', monitor_idx, trigger_bot_pos_rel_height)
                trigger_left  = Grid._horz_pos_string('TriggerLeft', monitor_idx, trigger_left_pos_rel_width)
                trigger_right = Grid._horz_pos_string('TriggerRight',  monitor_idx, trigger_right_pos_rel_width)
                # GRIDBOXES
                gridbox_top_pos_rel_height  = offset_top_rel_height + gridbox[0] / (self.h) / grids_in_monitor_y
                gridbox_bot_pos_rel_height  = offset_top_rel_height + (gridbox[1] + 1) / (self.h) / grids_in_monitor_y
                gridbox_left_pos_rel_width  = offset_left_rel_width + gridbox[2] / (self.w) / grids_in_monitor_x
                gridbox_right_pos_rel_width = offset_left_rel_width + (gridbox[3] + 1) / (self.w) / grids_in_monitor_x
                gridbox_top   = Grid._vert_pos_string('GridTop', monitor_idx, gridbox_top_pos_rel_height)
                gridbox_bot   = Grid._vert_pos_string('GridBottom', monitor_idx, gridbox_bot_pos_rel_height)
                gridbox_left  = Grid._horz_pos_string('GridLeft', monitor_idx, gridbox_left_pos_rel_width)
                gridbox_right = Grid._horz_pos_string('GridRight', monitor_idx, gridbox_right_pos_rel_width)

                grid_string = grid_string + "".join([monitor, trigger_top, trigger_bot, trigger_left, trigger_right, \
                                                     gridbox_top, gridbox_bot, gridbox_left, gridbox_right])
        return (grid_counter, grid_string)