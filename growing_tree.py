import random
import maze

CHOOSE     = 'newest'
#CHOOSE     = 'random'

class GrowingTree:

    def choose_index(self, ceil):
        if CHOOSE == 'newest':
            return ceil-1
        if CHOOSE == 'oldest':
            return 0
        if CHOOSE == 'random':
            return random.randint(0, ceil-1)
        # or implement your own!
        
    def grow_tree(self, grid, cell):
        #column, row = random.randint(0, grid.columns-1), random.randint(0, grid.rows-1)
        cells = []
        #cells = cells + [grid[column][row]]
        cells = cells + [grid.random_cell()]

        while cells:
            #print(grid)
            found_unvisited_neighbor = False
            index = self.choose_index(len(cells))
            #column, row = cells[index]

            cell = cells[index] # grid[column][row]
            neighbors = cell.get_available_neighbors()
            random.shuffle(neighbors)
            #print("choosing from: ", neighbors)
            for n in neighbors:
                #print("looking at: ", n, n.get_visited(), index)
                if not n.get_visited():
                    #print("linking!")
                    cell.link(n)
                    n.set_visited()
                    cell.set_visited()
                    cells = cells + [n] # [[n.column, n.row]]
                    found_unvisited_neighbor = True
                    break;

            if not found_unvisited_neighbor:
                #print("deleting", index)
                del cells[index]

    def find_unlinked_cells(self, grid):
        for cell in grid.each_cell():
            if (not cell.is_linked(cell.north()) and
                not cell.is_linked(cell.east()) and
                not cell.is_linked(cell.west()) and
                not cell.is_linked(cell.south())):
                return cell
        return False

    def build_maze(self, grid):
        cell = grid.random_cell()
        self.grow_tree(grid, cell)
        while cell:
            cell = self.find_unlinked_cells(grid)
            self.grow_tree(grid, cell)


    def __init__(self, grid):
        grid.reload_cells()
        

def main_rect():
    rows = 5
    cols = 5
    grid = maze.Grid(rows, cols)
    gt = GrowingTree(grid)
    gt.build_maze(grid)
    grid.to_svg()

def main_mask():
    rows = 10
    cols = 10
    m = maze.Mask.from_image("/Users/sanj/Desktop/saoirse_maze2.png");
    grid = maze.MaskedGrid(m) #Grid(rows, cols), m)
    gt = GrowingTree(grid)
    gt.build_maze(grid)
    grid.to_svg()

def ben_mask():
    m = maze.Mask.from_image("/Users/sanj/Desktop/marc.png");
    grid = maze.MaskedGrid(m) #Grid(rows, cols), m)
    gt = GrowingTree(grid)
    gt.build_maze(grid)
    grid.to_svg()

def main_test_mask():
    m = maze.Mask.from_image("/Users/sanj/Downloads/pixel-12x12.png")
    grid = maze.MaskedGrid(m)
    gt = GrowingTree(grid)
    gt.build_maze(grid)
    grid.to_svg()

if __name__ == "__main__":
    #main_mask()
    #main_test_mask()
    ben_mask()
        
