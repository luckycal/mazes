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

        self.__prepare_grid()
        self.__configure_cells()

    def __prepare_grid(self):
        for i in range(self.rows):
            self.grid.append([Cell(i, j) for j in range(self.columns)])

    def __configure_cells(self):
        for i in range(self.rows):
            for j in range(self.columns):
                cell = self.grid[i][j]
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
                    if  row[cellid].is_linked(row[cellid-1]):
                        eastboundary += " "
                    else:
                        eastboundary += "|"
                eastboundary += "   "

                if row[cellid].neighbors['south']:
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
        wall_width = 0
        top_offset = 0#wall_width
        left_offset = 0#wall_width
        img_width = cell_size * self.columns + top_offset * 2 + wall_width
        img_height = cell_size * self.rows + left_offset * 2 + wall_width
        dwg = svgwrite.Drawing('./exports/maze.svg', size=(img_width*mm, img_height*mm))
        
        for cell in self.each_cell():
            x1 = cell.column * cell_size + top_offset + wall_width
            y1 = cell.row * cell_size + left_offset + wall_width
            x2 = (cell.column + 1) * cell_size + top_offset
            y2 = (cell.row + 1) * cell_size + left_offset


            # outer walls
            if not cell.north():
                if not cell.west():
                    dwg.add(dwg.line(((x1-wall_width)*mm, (y1-wall_width)*mm),
                                     ((x2+wall_width)*mm, (y1-wall_width)*mm),
                                     stroke='black', stroke_width=1*mm))
                else:
                    dwg.add(dwg.line(((x1)*mm, (y1-wall_width)*mm),
                                     ((x2+wall_width)*mm, (y1-wall_width)*mm),
                                     stroke='black', stroke_width=1*mm))
                    
                if cell.is_linked(cell.east()):
                    dwg.add(dwg.line(((x1)*mm, (y1)*mm),
                                     ((x2+wall_width)*mm, (y1)*mm),
                                     stroke='black', stroke_width=1*mm))
                else:
                    dwg.add(dwg.line(((x1)*mm, (y1)*mm),
                                     ((x2)*mm, (y1)*mm),
                                     stroke='black', stroke_width=1*mm))
            if not cell.west():
                if not cell.north():
                    dwg.add(dwg.line(((x1-wall_width)*mm, (y1-wall_width)*mm),
                                     ((x1-wall_width)*mm, (y2)*mm),
                                     stroke='black', stroke_width=1*mm))
                else:
                    dwg.add(dwg.line(((x1-wall_width)*mm, (y1)*mm),
                                 ((x1-wall_width)*mm, (y2)*mm),
                                 stroke='black', stroke_width=1*mm))
                dwg.add(dwg.line(((x1)*mm, (y1)*mm),
                                 ((x1)*mm, (y2)*mm),
                                 stroke='black', stroke_width=1*mm))

            if not cell.east():
                if cell.is_linked(cell.south()):
                    dwg.add(dwg.line(((x2)*mm, (y2)*mm),
                                     ((x2)*mm, (y2+wall_width)*mm),
                                     stroke='black', stroke_width=1*mm))
                if not cell.north(): # top right corner
                    dwg.add(dwg.line(((x2+wall_width)*mm, (y1-wall_width)*mm),
                                     ((x2+wall_width)*mm, (y1)*mm),
                                     stroke='black', stroke_width=1*mm))
                dwg.add(dwg.line(((x2+wall_width)*mm, (y2)*mm),
                                 ((x2+wall_width)*mm, (y2+wall_width)*mm),
                                 stroke='black', stroke_width=1*mm))

                if not cell.south(): # bottom right corner
                    dwg.add(dwg.line(((x2)*mm, (y2+wall_width)*mm),
                                     ((x2+wall_width)*mm, (y2+wall_width)*mm),
                                     stroke='black', stroke_width=1*mm))

                
            # inner walls
            # south wall
            if not cell.is_linked(cell.east()):
                dwg.add(dwg.line(((x2)*mm, (y1)*mm),
                                 ((x2)*mm, (y2)*mm),
                                 stroke='black', stroke_width=1*mm))
                dwg.add(dwg.line(((x2+wall_width)*mm, (y1)*mm),
                                 ((x2+wall_width)*mm, (y2)*mm),
                                 stroke='black', stroke_width=1*mm))

            # east wall
            if not cell.is_linked(cell.south()):
                dwg.add(dwg.line(((x1)*mm, (y2)*mm),
                                 ((x2)*mm, (y2)*mm),
                                stroke='black', stroke_width=1*mm))
                dwg.add(dwg.line(((x1)*mm, (y2+wall_width)*mm),
                                 ((x2)*mm, (y2+wall_width)*mm),
                                 stroke='black', stroke_width=1*mm))

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
                cell.south() and cell.south().west() and cell.south().is_linked(cell.south().west()) and
                cell.west() and cell.west().south() and cell.west().is_linked(cell.west().south())):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2)*mm),
                                ((x1-wall_width)*mm, (y2+wall_width)*mm),
                                 stroke='black', stroke_width=1*mm))
            if (cell.is_linked(cell.south()) and
                ((not cell.is_linked(cell.west())) or
                (cell.south() and cell.south().west() and (not cell.south().is_linked(cell.south().west()))))):
                dwg.add(dwg.line(((x1)*mm, (y2)*mm),
                                ((x1)*mm, (y2+wall_width)*mm),
                                 stroke='black', stroke_width=1*mm))

            # should we fill 3
            if (cell.is_linked(cell.south()) and
                cell.is_linked(cell.west()) and
                cell.south() and cell.south().west() and cell.south().is_linked(cell.south().west()) and
                cell.west() and cell.west().south() and (not cell.west().is_linked(cell.west().south()))):
                dwg.add(dwg.line(((x1)*mm, (y2)*mm),
                                ((x1)*mm, (y2+wall_width)*mm),
                                 stroke='black', stroke_width=1*mm))
            if ((cell.west() and cell.west().south() and cell.west().is_linked(cell.west().south())) and
                ((not cell.is_linked(cell.west())) or
                 (cell.south() and cell.south().west() and (not cell.south().is_linked(cell.south().west()))))):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2)*mm),
                                ((x1-wall_width)*mm, (y2+wall_width)*mm),
                                 stroke='black', stroke_width=1*mm))
            if (not cell.west()):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2)*mm),
                                ((x1-wall_width)*mm, (y2+wall_width)*mm),
                                 stroke='black', stroke_width=1*mm))
            
            # should we fill 2
            if (cell.is_linked(cell.south()) and cell.is_linked(cell.west()) and
                cell.west() and cell.west().south() and cell.west().is_linked(cell.west().south()) and
                cell.south() and cell.south().west() and (not cell.south().is_linked(cell.south().west()))):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2)*mm),
                                ((x1)*mm, (y2)*mm),
                                 stroke='black', stroke_width=1*mm))
            if (cell.south() and cell.south().west() and cell.south().is_linked(cell.south().west()) and
                ((not cell.is_linked(cell.south())) or
                 (cell.west() and cell.west().south() and (not cell.west().is_linked(cell.west().south()))))):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2+wall_width)*mm),
                                ((x1)*mm, (y2+wall_width)*mm),
                                 stroke='black', stroke_width=1*mm))
            if (not cell.south()):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2+wall_width)*mm),
                                ((x1)*mm, (y2+wall_width)*mm),
                                 stroke='black', stroke_width=1*mm))
            
            # should we fill 4
            if (cell.is_linked(cell.south()) and cell.south() and cell.south().is_linked(cell.south().west()) and
                cell.west() and cell.west().south() and cell.west().is_linked(cell.west().south()) and
                cell.west() and (not cell.is_linked(cell.west()))):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2+wall_width)*mm),
                                ((x1)*mm, (y2+wall_width)*mm),
                                 stroke='black', stroke_width=1*mm))
            if (cell.west() and cell.is_linked(cell.west()) and
                ((not cell.is_linked(cell.south())) or
                 (cell.west() and cell.west().south() and (not cell.west().is_linked(cell.west().south()))))):
                dwg.add(dwg.line(((x1-wall_width)*mm, (y2)*mm),
                                ((x1)*mm, (y2)*mm),
                                 stroke='black', stroke_width=1*mm))
            

        dwg.save()


        


if __name__ == '__main__':
    pass
