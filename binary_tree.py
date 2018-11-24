import random
import maze

class BinaryTree:

    def build_maze(self, grid):
        for cell in grid.each_cell():
            neighbors = []
            n = cell.get_neighbors()
            if n['north']:
                neighbors.append(n['north'])
            if n['east']:
                neighbors.append(n['east'])
            if neighbors:
                cell.link(random.choice(neighbors))

    def __init__(self, grid):
        grid.reload_cells()
        

def main():
    grid = maze.Grid(10,10)
    bt = BinaryTree(grid)
    bt.build_maze(grid)
    print(grid)

if __name__ == "__main__":
    main()
        
