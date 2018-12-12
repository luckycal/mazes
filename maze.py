import random
import svgwrite
from svgwrite import cm, mm   

class Cell:

    def __init__(self, row, column):

        self.row = row
        self.column = column

        self.links = {}
        self.visited = False
        self.neighbors = {'north': None, 'south': None, 'east': None, 'west': None}

    def north(self):
        return self.neighbors['north']
    
    def south(self):
        return self.neighbors['south']
    
    def east(self):
        return self.neighbors['east']
    
    def west(self):
        return self.neighbors['west']
    
    def get_neighbors(self):
        return self.neighbors

    def get_available_neighbors(self):
        ret = []
        for dir in self.neighbors:
            if self.neighbors[dir]:
                ret = ret + [self.neighbors[dir]]
        return ret

    def set_neighbors(self, key, value=None):
        self.neighbors[key] = value

    def get_visited(self):
        return self.visited

    def set_visited(self):
        self.visited = True

    def clear_visited(self):
        self.visited = False

    def link(self, cell, bidi=True):
        self.links[cell] = True
        if bidi:
            cell.link(self, False)

    def unlink(self, cell, bidi=True):
        del self.links[cell]
        if bidi:
            cell.unlink(self, False)

    def get_links(self):
        return tuple(self.links.keys())

    def is_linked(self, cell):
        return self.links.get(cell, False)

    def __repr__(self):
        return "Cell(%r,%r)" % (self.row, self.column)

    def __str__(self):
        return "Cell row %s column %s" % (self.row, self.column)


class Grid:

    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.grid = []

        self.rowcount = 0
        self.cellcount = 0

        self.prepare_grid()
        self.configure_cells()
                    
    def prepare_grid(self):
        for i in range(self.rows):
            self.grid.append([Cell(i, j) for j in range(self.columns)])

    def configure_cells(self):
        for i in range(self.rows):
            for j in range(self.columns):
                cell = self.grid[i][j]
                if not cell == None:
                    cell.set_neighbors('north', value=self[cell.row-1, cell.column])
                    cell.set_neighbors('south', value=self[cell.row+1, cell.column])
                    cell.set_neighbors('west', value=self[cell.row, cell.column-1])
                    cell.set_neighbors('east', value=self[cell.row, cell.column+1])

    def __getitem__(self, key):
        if type(key)==int:
            if 0 <= key < self.rows and 0 <= key < self.columns:
                return self.grid[key]
        else:
            if 0 <= key[0] < self.rows and 0 <= key[1] < self.columns:
                return self.grid[key[0]][key[1]]

    def random_cell(self):
        return self[random.randrange(0, self.rows), random.randrange(0, self.columns)]

    def __len__(self):
        return self.rows*self.columns

    def each_row(self, forward=True):
        if forward:
            while self.rowcount < self.rows:
                self.rowcount += 1
                yield self.grid[self.rowcount-1]
        else:
            while self.rowcount > 0:
                self.rowcount -= 1
                yield self.grid[self.rowcount]

    def reload_rows(self):
        self.rowcount = 0

    def each_cell(self, forward=True):
        if forward:
            while self.cellcount < len(self):
                self.cellcount +=1
                yield self.grid[(self.cellcount-1)//self.rows][(self.cellcount-1) % self.columns]
        else:
            while self.cellcount > 0:
                self.cellcount -=1
                yield self.grid[(self.cellcount)//self.rows][(self.cellcount) % self.columns]

    def each_row(self):
        """
        Iterate over each row in the grid
        """
        for row in self.grid:
            yield row
            
    def each_cell(self):
        """
                Iterator over all cells in the grid
        """
        for row in self.each_row():
            for cell in row:
                # Need the if clause for masked grids where a cell might or not 
                # be present at a specific (row, column)
                if cell:
                    yield cell
                    
                    
    def reload_cells(self):
        self.cellcount = 0

    def contents_of(self, cell):
        return " "

    def background_color_for(self, cell):
        return None

    def __repr__(self):
        return "Grid (%r,%r)" % (self.rows, self.columns)

    def __str__(self):
        #return "Grid row %s column %s" % (self.rows, self.columns)
        output = "+" + "---+" * self.columns +"\n"
        self.reload_rows()
        for row in self.each_row():
            eastboundary = ""
            southboundary = ""
            for cellid in range(len(row)):

                if cellid == 0:
                    eastboundary +="|"
                else:
                    if row[cellid] and  row[cellid].is_linked(row[cellid-1]):
                        eastboundary += " "
                    else:
                        eastboundary += "|"
                eastboundary += "   "

                if row[cellid] and row[cellid].neighbors['south']:
                    if row[cellid].is_linked(row[cellid].neighbors['south']):
                        southboundary += "+   "
                    else:
                        southboundary += "+---"
                else:
                    southboundary += "+---"

            eastboundary += "|\n"
            southboundary += "+\n"

            output += eastboundary
            output += southboundary

        return output


    def to_svg(self, cell_size = 10):
        wall_width = 2
        top_offset = 0#wall_width
        left_offset = 0#wall_width
        outer_wall_color = 'red'
        inner_wall_color = 'black'
        draw_outer_walls = True
        img_width = cell_size * self.columns + top_offset * 2 + wall_width
        img_height = cell_size * self.rows + left_offset * 2 + wall_width
        dwg = svgwrite.Drawing('./exports/maze.svg', size=(img_width*mm, img_height*mm))
        
        for cell in self.each_cell():
            x1 = cell.column * cell_size + top_offset + wall_width
            y1 = cell.row * cell_size + left_offset + wall_width
            x2 = (cell.column + 1) * cell_size + top_offset
            y2 = (cell.row + 1) * cell_size + left_offset

            #print(cell)

            if draw_outer_walls:
                # outermost walls
                if not cell.north():
                    if not cell.west():
                        if cell.east() and cell.east().north():
                            dwg.add(dwg.line(((x1-wall_width)*mm, (y1-wall_width)*mm),
                                             ((x2)*mm, (y1-wall_width)*mm),
                                             stroke=outer_wall_color, stroke_width=1*mm))
                        else:
                            dwg.add(dwg.line(((x1-wall_width)*mm, (y1-wall_width)*mm),
                                             ((x2+wall_width)*mm, (y1-wall_width)*mm),
                                             stroke=outer_wall_color, stroke_width=1*mm))
                    else: # there is a cell to the west
                        if cell.east() and cell.east().north():
                            dwg.add(dwg.line(((x1)*mm, (y1-wall_width)*mm),
                                             ((x2)*mm, (y1-wall_width)*mm),
                                             stroke=outer_wall_color, stroke_width=1*mm))
                        else:
                            dwg.add(dwg.line(((x1)*mm, (y1-wall_width)*mm),
                                             ((x2+wall_width)*mm, (y1-wall_width)*mm),
                                             stroke=outer_wall_color, stroke_width=1*mm))
                        
                if not cell.west():
                    if not cell.north():
                        dwg.add(dwg.line(((x1-wall_width)*mm, (y1-wall_width)*mm),
                                         ((x1-wall_width)*mm, (y2)*mm),
                                         stroke=outer_wall_color, stroke_width=1*mm))
                    else:
                        dwg.add(dwg.line(((x1-wall_width)*mm, (y1)*mm),
                                         ((x1-wall_width)*mm, (y2)*mm),
                                         stroke=outer_wall_color, stroke_width=1*mm))
                    if (not cell.west() and not (cell.south() and cell.south().west())):
                        dwg.add(dwg.line(((x1-wall_width)*mm, (y2)*mm),
                                         ((x1-wall_width)*mm, (y2+wall_width)*mm),
                                         stroke=outer_wall_color, stroke_width=1*mm))

                if not cell.east():
                    if not cell.north(): # top right corner
                        dwg.add(dwg.line(((x2+wall_width)*mm, (y1-wall_width)*mm),
                                         ((x2+wall_width)*mm, (y1)*mm),
                                         stroke=outer_wall_color, stroke_width=1*mm))

                    if not(cell.south() and cell.south().east()):
                        dwg.add(dwg.line(((x2+wall_width)*mm, (y2)*mm),
                                         ((x2+wall_width)*mm, (y2+wall_width)*mm),
                                         stroke=outer_wall_color, stroke_width=1*mm))
                        
                    if not cell.south(): # bottom right corner
                        dwg.add(dwg.line(((x2)*mm, (y2+wall_width)*mm),
                                         ((x2+wall_width)*mm, (y2+wall_width)*mm),
                                         stroke=outer_wall_color, stroke_width=1*mm))
                    
                if not cell.south():
                    dwg.add(dwg.line(((x1)*mm, (y2+wall_width)*mm),
                                     ((x2)*mm, (y2+wall_width)*mm),
                                     stroke=outer_wall_color, stroke_width=1*mm))
                    if (not (cell.west() and cell.west().south())):
                        dwg.add(dwg.line(((x1-wall_width)*mm, (y2+wall_width)*mm),
                                         ((x1)*mm, (y2+wall_width)*mm),
                                         stroke=outer_wall_color, stroke_width=1*mm))

                if not cell.east():
                    dwg.add(dwg.line(((x2+wall_width)*mm, (y1)*mm),
                                     ((x2+wall_width)*mm, (y2)*mm),
                                     stroke=outer_wall_color, stroke_width=1*mm))

                    
            # inner walls
            # east wall
            if not cell.is_linked(cell.east()):
                dwg.add(dwg.line(((x2)*mm, (y1)*mm),
                                 ((x2)*mm, (y2)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))
                if cell.east():
                    dwg.add(dwg.line(((x2+wall_width)*mm, (y1)*mm),
                                     ((x2+wall_width)*mm, (y2)*mm),
                                     stroke=inner_wall_color, stroke_width=1*mm))

            # south wall
            if not cell.is_linked(cell.south()):
                dwg.add(dwg.line(((x1)*mm, (y2)*mm),
                                 ((x2)*mm, (y2)*mm),
                                stroke=inner_wall_color, stroke_width=1*mm))
                if cell.south():
                    dwg.add(dwg.line(((x1)*mm, (y2+wall_width)*mm),
                                     ((x2)*mm, (y2+wall_width)*mm),
                                     stroke=inner_wall_color, stroke_width=1*mm))

            if not cell.east() and cell.south() and cell.south().east() and cell.south().is_linked(cell.south().east()):
                dwg.add(dwg.line(((x2)*mm, (y2+wall_width)*mm),
                                 ((x2+wall_width)*mm, (y2+wall_width)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))

            if not cell.north():
                if cell.is_linked(cell.east()):
                    dwg.add(dwg.line(((x1)*mm, (y1)*mm),
                                     ((x2+wall_width)*mm, (y1)*mm),
                                     stroke=inner_wall_color, stroke_width=1*mm))
                else:
                    dwg.add(dwg.line(((x1)*mm, (y1)*mm),
                                     ((x2)*mm, (y1)*mm),
                                     stroke=inner_wall_color, stroke_width=1*mm))
                
            if not cell.east():
                if cell.is_linked(cell.south()):
                    dwg.add(dwg.line(((x2)*mm, (y2)*mm),
                                     ((x2)*mm, (y2+wall_width)*mm),
                                     stroke=inner_wall_color, stroke_width=1*mm))

            if not cell.west():
                dwg.add(dwg.line(((x1)*mm, (y1)*mm),
                                 ((x1)*mm, (y2)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))



            # fill in intersections
            #
            #     4
            #   +---+
            # 3 |   | 1
            #   +---+
            #     2

            # should we fill 1
            if (not cell.is_linked(cell.south()) and
                cell.is_linked(cell.west()) and
                cell.south() and cell.south().is_linked(cell.south().west()) and
                cell.west() and cell.west().is_linked(cell.west().south())):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2)*mm),
                                ((x1-wall_width)*mm, (y2+wall_width)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))
            if (cell.is_linked(cell.south()) and
                ((not cell.is_linked(cell.west())) or (not cell.west()) or
                (cell.south() and (not cell.south().is_linked(cell.south().west()))))):
                dwg.add(dwg.line(((x1)*mm, (y2)*mm),
                                ((x1)*mm, (y2+wall_width)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))

            # should we fill 3
            if (cell.is_linked(cell.south()) and
                cell.is_linked(cell.west()) and
                cell.south() and cell.south().is_linked(cell.south().west()) and
                cell.west() and (not cell.west().is_linked(cell.west().south()))):
                dwg.add(dwg.line(((x1)*mm, (y2)*mm),
                                ((x1)*mm, (y2+wall_width)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))
            if ((cell.west() and cell.west().is_linked(cell.west().south())) and
                ((not cell.is_linked(cell.west())) or (not cell.south()) or
                 (cell.south() and (not cell.south().is_linked(cell.south().west()))))):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2)*mm),
                                ((x1-wall_width)*mm, (y2+wall_width)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))
            
            # should we fill 2
            if (cell.is_linked(cell.south()) and cell.is_linked(cell.west()) and
                cell.west() and cell.west().is_linked(cell.west().south()) and
                cell.south() and (not cell.south().is_linked(cell.south().west()))):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2)*mm),
                                ((x1)*mm, (y2)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))
            if (cell.south() and cell.south().is_linked(cell.south().west()) and
                ((not cell.is_linked(cell.south())) or (not cell.west()) or
                 (cell.west() and (not cell.west().is_linked(cell.west().south()))))):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2+wall_width)*mm),
                                ((x1)*mm, (y2+wall_width)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))
            
            # should we fill 4
            if (cell.is_linked(cell.south()) and cell.south() and cell.south().is_linked(cell.south().west()) and
                cell.west()  and cell.west().is_linked(cell.west().south()) and
                cell.west() and (not cell.is_linked(cell.west()))):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2+wall_width)*mm),
                                ((x1)*mm, (y2+wall_width)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))
            if (cell.west() and cell.is_linked(cell.west()) and
                ((not cell.is_linked(cell.south())) or (not cell.west()) or
                 (cell.west() and (not cell.west().is_linked(cell.west().south()))))):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2)*mm),
                                ((x1)*mm, (y2)*mm),
                                 stroke=inner_wall_color, stroke_width=1*mm))
            

        dwg.save()


        
class MaskedGrid(Grid):
    def __init__(self, mask):
        self.mask = mask
        super(MaskedGrid, self).__init__(mask.n_rows, mask.n_columns)

    
    # Overriden method from Grid class
    def prepare_grid(self):
        print("preparing masked grid")
        for i in range(self.rows):
            self.grid.append([Cell(i, j) if self.mask[i, j] else None for j in range(self.columns)])
                                                                
    def random_cell(self):
        row, col = self.mask.random_location()
        return self.grid[row][col]


class Mask:
    def __init__(self, n_rows, n_columns):
        self.n_rows = n_rows
        self.n_columns = n_columns
        self.bits = [[True for _ in range(n_columns)] for _ in range(n_rows)]

    def __getitem__(self, pos):
        """ Get a Boolean value from this mask for the specified position """
        row, column = pos
        if row <= self.n_rows-1 and column <= self.n_columns-1:
            return self.bits[row][column]
        else:
            return False
        
    def __setitem__(self, pos, is_on):
        """ Set a Boolean value in this Mask at specified position """
        row, column = pos
        self.bits[row][column] = is_on

    def count(self):
        """ Count the number of True values in this mask """
        return sum([self.bits[x][y] for x in range(self.n_rows)
                                    for y in range(self.n_columns)])

    def random_location(self):
        while True:
            row = random.randint(0, self.n_rows-1)
            col = random.randint(0, self.n_columns-1)
            if self.bits[row][col]:
                return row, col

    def __str__(self):
        ret = ""
        for row in range(0, self.n_rows):
            for col in range(0, self.n_columns):
                if self.bits[row][col]:
                    ret = ret + "."
                else:
                    ret = ret + "X"
            ret = ret + "\n"
        return ret

    @staticmethod
    def from_image(img_file):
        import pygame
        surface = pygame.image.load(img_file)
        mask = Mask(surface.get_height(), surface.get_width())
        print("mask ")
        print(surface.get_height())
        print(surface.get_width())
        for row in range(0, mask.n_rows):
            for col in range(0, mask.n_columns):
                color = surface.get_at((col, row))
                if color.r <= 50 and color.g <= 50 and color.b <= 50:
                    mask[row, col] = False
                else:
                    mask[row, col] = True
        return mask

if __name__ == '__main__':
    pass
