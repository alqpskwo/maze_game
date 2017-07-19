from random import shuffle, choice
from pdb import set_trace

class Maze(object):
    WIDTH_MIN = 3
    HEIGHT_MIN = 3

    def __init__(self, width, height):

        if not (Maze.WIDTH_MIN <= width and width % 2 == 1):
            message = "width must be odd and greater than{}.".format(
                Maze.WIDTH_MIN)
            raise ValueError(message)

        if not (Maze.HEIGHT_MIN <= height and height % 2 == 1):
            message = "height must be odd and greater than{}.".format(
                Maze.HEIGHT_MIN)
            raise ValueError(message)

        self.width = width - 1
        self.height = height - 1

        self.cells =[[x % 2 == 0 or y % 2 == 0
                      for y in range(0, self.height)]
                      for x in range(0, self.width)]

    def generate(self):
        walls = []
        regions = {}

        for x in range(0, self.width):
            for y in range(0, self.height):
                if x % 2 != y % 2:
                    walls.append((x,y))
                elif not self.cells[x][y]:
                    regions[(x,y)] = [(x,y)]

        shuffle(walls)

        while walls:
            wall_x, wall_y = walls.pop()

            # Find the pair of rooms the wall separates.
            if wall_x % 2 == 0:
                room1 = ( (wall_x - 1) % self.width, wall_y)
                room2 = ( (wall_x + 1) % self.width, wall_y)
            else:
                room1 = (wall_x, (wall_y - 1) % self.height)
                room2 = (wall_x, (wall_y + 1) % self.height)

            # If the walls are not already connected, delete the wall.
            if not room2 in regions[room1]:
                self.cells[wall_x][wall_y] = False
                region = regions[room1] + regions[room2]
                for room in region:
                    regions[room] = region

    def __repr__(self):
        s = ""
        for y in range(0, self.height):
            for x in range(0, self.width):
                s += '#' if self.cells[x][y] else ' '
            s += '\n'

        return s

    def get_wall_segments(self):
        wall_segments = []
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.cells[x][y]:
                    if self.cells[(x + 1) % self.width][y]:
                        wall_segments.append((x,y,(x + 1) % self.width,y))
                    if self.cells[x][(y + 1) % self.height]:
                        wall_segments.append((x,y,x,(y+1) % self.height))
        return wall_segments

    def get_empty_cells(self):
        cells = []
        for y in range(0, self.height):
            for x in range(0, self.width):
                if not self.cells[x][y]:
                    cells.append((x,y))
        shuffle(cells)
        return cells

    def is_empty(self, x, y):
            return not self.cells[x][y]

    def neighbor(self, x, y, direction):
        if direction == 'up':
            return(x, (y + 1) % self.height)
        elif direction == 'right':
            return((x + 1) % self.width, y)
        elif direction == 'down':
            return(x, (y - 1) % self.height)
        elif direction == 'left':
            return((x - 1) % self.width, y)

class GameObject(object):
    def __init__(self, x, y, maze):
        self.x = x
        self.y = y
        self.maze = maze
        self.marked_for_removal = False

    def collide(self, player):
        pass


class Player(GameObject):
    def __init__(self, x, y, maze):
        super(Player, self).__init__(x, y, maze)
        self.gold = False
        self.has_crystal = False

    def move(self, direction):
        neighbor = self.maze.neighbor(self.x, self.y, direction)
        if self.maze.is_empty(*neighbor):
            self.x, self.y = neighbor

class Enemy(GameObject):
    def __init__(self, x, y, maze):
        super(Enemy, self).__init__(x, y, maze)
        self.prev_loc = (x, y)


    def move(self, *args):
        neighbors = [self.maze.neighbor(self.x, self.y, direction)
            for direction in ['up', 'down', 'left', 'right']]
        candidates = [cell for cell in neighbors 
            if self.maze.is_empty(*cell) and cell != self.prev_loc]

        self.prev_loc = (self.x, self.y)
        if candidates:
            self.x, self.y = choice(candidates)

    def collide(self, player):
        if player.has_crystal:
            self.marked_for_removal = True
            player.has_crystal = False
        else:
            player.marked_for_removal = True

class Gold(GameObject):
    def collide(self, player):
        player.gold += 1
        self.marked_for_removal = True

class Crystal(GameObject):
    def collide(self, player):
        if not player.has_crystal:
            player.has_crystal = True
            self.marked_for_removal = True

