from Grid import Grid
import os

inpath = os.path.abspath("example_psd\\test.psd")
grid = Grid(inpath)
grid.print()

print()
print()

grid_counter, grid_string = grid.get_grid_string(0,0,1,1,0,0)
print('n grids = ', grid_counter + 1)
print()
print(grid_string)

print("fin")