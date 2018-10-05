from Grid import Grid


def compute_gridstr(monitor_layouts, psd_paths) -> str:
    grids = {} # maps grid indices to actual grids
    result = ""
    sub_grid_id = 1 # the id of the possible windowpositions / triggers
    for ml in monitor_layouts:
        mlh = ml.h
        mlw = ml.w
        for y in range(ml.h):
            for x in range(ml.w):
                grid_id = ml.get_grid_id(x,y)
                if grid_id >= 0:
                    # compute grid
                    if not(grid_id in grids.keys()):
                        grids[grid_id] = Grid(psd_paths[grid_id])
                    grid = grids[grid_id]

                    # build grid string
                    sgi, grid_string = grid.get_grid_string(ml.monitor_id, sub_grid_id, ml.w, ml.h, x, y)
                    sub_grid_id = sgi + 1
                    result += grid_string

    result = '[Groups]\n  NumberOfGroups = {0}\n'.format(sub_grid_id-1) + result
    return result